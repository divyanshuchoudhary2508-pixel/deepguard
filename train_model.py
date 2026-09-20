import os
import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("deepguard.train")

def train_deepfake_model(dataset_dir, output_model_path, epochs=15, batch_size=32, lr=0.0001):
    """
    Paper-aligned fine-tuning script based on IEEE TENCON 2024 paper recipe:
    - Base Model: DenseNet121 / Xception
    - Augmentation: rotation, width/height shift, shear, zoom, horizontal flip
    - Preprocessing: 224x224, rescale [0, 1]
    - Head: GlobalAveragePooling -> Dense(256, ReLU) -> Dropout(0.25) -> Dense(1, Sigmoid)
    - Optimizer: Adam (lr=0.0001), Loss: BinaryCrossEntropy
    """
    import tensorflow as tf
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

    dataset_path = Path(dataset_dir)
    train_dir = dataset_path / "train"
    val_dir = dataset_path / "val" if (dataset_path / "val").exists() else train_dir

    if not train_dir.exists():
        logger.error(f"Training directory '{train_dir}' does not exist!")
        logger.info("Expected dataset structure:\n  dataset_dir/\n    ├── train/\n    │   ├── REAL/\n    │   └── FAKE/\n    └── val/\n        ├── REAL/\n        └── FAKE/")
        return False

    logger.info("Setting up ImageDataGenerators with paper augmentations...")
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        validation_split=0.15 if train_dir == val_dir else 0.0
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    if train_dir == val_dir:
        train_gen = train_datagen.flow_from_directory(
            str(train_dir),
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='training'
        )
        val_gen = train_datagen.flow_from_directory(
            str(train_dir),
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary',
            subset='validation'
        )
    else:
        train_gen = train_datagen.flow_from_directory(
            str(train_dir),
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary'
        )
        val_gen = val_datagen.flow_from_directory(
            str(val_dir),
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode='binary'
        )

    logger.info(f"Detected classes: {train_gen.class_indices}")

    logger.info("Building base DenseNet121 architecture...")
    base_model = tf.keras.applications.DenseNet121(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze base layers for initial warm-up
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D(name='global_average_pooling2d')(x)
    x = tf.keras.layers.BatchNormalization(name='batch_normalization')(x)
    x = tf.keras.layers.Dropout(0.25, name='dropout')(x)
    x = tf.keras.layers.Dense(256, activation='relu', name='dense')(x)
    x = tf.keras.layers.BatchNormalization(name='batch_normalization_1')(x)
    x = tf.keras.layers.Dropout(0.25, name='dropout_1')(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid', name='dense_1')(x)

    model = tf.keras.Model(inputs=base_model.input, outputs=outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )

    checkpoint = ModelCheckpoint(
        filepath=str(output_model_path),
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )

    early_stop = EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1)

    logger.info(f"Starting training on {train_gen.samples} samples for {epochs} epochs...")
    history = model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=[checkpoint, early_stop, reduce_lr]
    )

    logger.info(f"Training complete! Best model saved to: {output_model_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DeepGuard Paper-Aligned GPU Training Script")
    parser.add_argument("--dataset_dir", type=str, required=True, help="Path to dataset root folder containing train/ and val/ subdirectories")
    parser.add_argument("--output_model", type=str, default=r"..\Models\model.h5", help="Path to save trained .h5 model file")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.0001, help="Learning rate")

    args = parser.parse_args()
    train_deepfake_model(args.dataset_dir, args.output_model, args.epochs, args.batch_size, args.lr)
