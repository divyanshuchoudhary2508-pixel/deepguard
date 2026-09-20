"""
Kaggle 2x T4 GPU Deepfake Detection Model Trainer for DeepGuard
===============================================================
Designed for Kaggle Notebooks with T4 x2 GPU Acceleration.
Uses TensorFlow tf.distribute.MirroredStrategy + Mixed Precision (fp16) + 2-Phase Transfer Learning.

Exported weights ('model.h5') can be dropped directly into DeepGuard backend.
"""

import os
import glob
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import DenseNet121
from sklearn.model_selection import train_test_split

print(f"TensorFlow Version: {tf.__version__}")
gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs Available: {len(gpus)}")
for gpu in gpus:
    print(f" - {gpu}")

# Enable Mixed Precision for 2x T4 Tensor Cores Speedup
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Multi-GPU Mirrored Strategy
strategy = tf.distribute.MirroredStrategy()
print(f"Number of devices in MirroredStrategy: {strategy.num_replicas_in_sync}")

# Configuration & Hyperparameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 64 * strategy.num_replicas_in_sync  # e.g., 128 for 2 GPUs
EPOCHS_PHASE1 = 8
EPOCHS_PHASE2 = 5
MODEL_SAVE_PATH = "model.h5"

def prepare_dataset_from_kaggle_input():
    """
    Scans Kaggle input directories for real vs fake images.
    Returns (train_df, val_df, test_df) DataFrames with 'filename' and 'class'.
    """
    kaggle_input = "/kaggle/input"
    all_files = glob.glob(os.path.join(kaggle_input, "**", "*.*"), recursive=True)
    image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Total image files discovered in Kaggle input: {len(image_files)}")

    real_paths = [f for f in image_files if "real" in f.lower() or "celeba" in f.lower()]
    fake_paths = [f for f in image_files if "fake" in f.lower() or "morphed" in f.lower() or "synthetic" in f.lower()]

    print(f"Real images found: {len(real_paths)}")
    print(f"Fake images found: {len(fake_paths)}")

    # Balance if necessary
    min_count = min(len(real_paths), len(fake_paths))
    if min_count > 0:
        real_paths = real_paths[:min_count]
        fake_paths = fake_paths[:min_count]

    data = []
    for p in real_paths:
        data.append({"filename": p, "class": "REAL"})
    for p in fake_paths:
        data.append({"filename": p, "class": "FAKE"})

    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    train_df, test_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df["class"])
    train_df, val_df = train_test_split(train_df, test_size=0.15, random_state=42, stratify=train_df["class"])

    print(f"Split sizes: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    return train_df, val_df, test_df


def build_densenet_model():
    """Builds DenseNet121 with Multi-GPU Mirrored Strategy context."""
    with strategy.scope():
        base_model = DenseNet121(
            include_top=False,
            weights="imagenet",
            input_shape=(*IMG_SIZE, 3)
        )
        base_model.trainable = False  # Freeze backbone for Phase 1

        inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
        # Data Augmentation layer built into graph for GPU execution
        x = layers.RandomFlip("horizontal")(inputs)
        x = layers.RandomRotation(0.1)(x)
        x = layers.RandomZoom(0.1)(x)
        
        # Normalization
        x = tf.keras.applications.densenet.preprocess_input(x)
        
        x = base_model(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)

        x = layers.Dense(256, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)

        # Output float32 for mixed precision stability
        outputs = layers.Dense(1, activation="sigmoid", dtype="float32")(x)

        model = models.Model(inputs, outputs, name="DeepGuard_DenseNet121")
        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-3),
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
        )

    return model, base_model


def main():
    print("=== DeepGuard 2x T4 GPU Training Protocol ===")
    train_df, val_df, test_df = prepare_dataset_from_kaggle_input()

    # Image Data Generators
    datagen = tf.keras.preprocessing.image.ImageDataGenerator()

    train_gen = datagen.flow_from_dataframe(
        train_df,
        x_col="filename",
        y_col="class",
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary"
    )

    val_gen = datagen.flow_from_dataframe(
        val_df,
        x_col="filename",
        y_col="class",
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary"
    )

    model, base_model = build_densenet_model()
    model.summary()

    # Callbacks
    cb_list = [
        callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor="val_auc", mode="max", verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, verbose=1),
        callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1)
    ]

    print("\n--- PHASE 1: Training Classification Head ---")
    history_p1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE1,
        callbacks=cb_list
    )

    print("\n--- PHASE 2: Unfreezing Top Backbone Layers & Fine-Tuning ---")
    with strategy.scope():
        base_model.trainable = True
        # Freeze initial 300 layers, fine-tune last block
        for layer in base_model.layers[:-30]:
            layer.trainable = False

        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-5),
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
        )

    history_p2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_PHASE2,
        callbacks=cb_list
    )

    print(f"\nTraining Complete! Best model saved to: {os.path.abspath(MODEL_SAVE_PATH)}")

if __name__ == "__main__":
    main()
