import json
import os

nb_code = '''import os
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

# Enable Mixed Precision (fp16) for Tensor Cores Speedup
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Multi-GPU Mirrored Strategy
strategy = tf.distribute.MirroredStrategy()
print(f"Number of devices in MirroredStrategy: {strategy.num_replicas_in_sync}")

# Settings & Parameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 64 * max(1, strategy.num_replicas_in_sync)
EPOCHS_PHASE1 = 8
EPOCHS_PHASE2 = 5
MODEL_SAVE_PATH = 'model.h5'

def scan_kaggle_dataset():
    kaggle_input = '/kaggle/input'
    all_files = glob.glob(os.path.join(kaggle_input, '**', '*.*'), recursive=True)
    image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f'Total images found across Kaggle datasets: {len(image_files)}')
    
    real_paths, fake_paths = [], []
    for f in image_files:
        f_lower = f.lower()
        if 'real' in f_lower or 'celeba' in f_lower or '/1/' in f_lower or 'authentic' in f_lower:
            real_paths.append(f)
        elif 'fake' in f_lower or 'morphed' in f_lower or 'synthetic' in f_lower or '/0/' in f_lower or 'manipulated' in f_lower:
            fake_paths.append(f)
            
    print(f'Discovered REAL images: {len(real_paths)}')
    print(f'Discovered FAKE images: {len(fake_paths)}')
    
    min_count = min(len(real_paths), len(fake_paths))
    if min_count > 0:
        # Cap to 20,000 max per class for balanced fast Kaggle run
        cap = min(20000, min_count)
        real_paths = real_paths[:cap]
        fake_paths = fake_paths[:cap]
        
    data = []
    for p in real_paths:
        data.append({'filename': p, 'class': 'REAL'})
    for p in fake_paths:
        data.append({'filename': p, 'class': 'FAKE'})
        
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    train_df, test_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df['class'])
    train_df, val_df = train_test_split(train_df, test_size=0.15, random_state=42, stratify=train_df['class'])
    
    print(f'Split summary: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}')
    return train_df, val_df, test_df

train_df, val_df, test_df = scan_kaggle_dataset()

datagen = tf.keras.preprocessing.image.ImageDataGenerator()
train_gen = datagen.flow_from_dataframe(
    train_df, x_col='filename', y_col='class',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='binary'
)
val_gen = datagen.flow_from_dataframe(
    val_df, x_col='filename', y_col='class',
    target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='binary'
)

def build_model():
    with strategy.scope():
        base_model = DenseNet121(include_top=False, weights='imagenet', input_shape=(*IMG_SIZE, 3))
        base_model.trainable = False
        
        inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
        x = layers.RandomFlip('horizontal')(inputs)
        x = layers.RandomRotation(0.1)(x)
        x = tf.keras.applications.densenet.preprocess_input(x)
        
        x = base_model(x, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)
        
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)
        
        outputs = layers.Dense(1, activation='sigmoid', dtype='float32')(x)
        
        model = models.Model(inputs, outputs, name='DeepGuard_DenseNet121')
        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-3),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
    return model, base_model

model, base_model = build_model()
model.summary()

cb_list = [
    callbacks.ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='val_auc', mode='max', verbose=1),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1),
    callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True, verbose=1)
]

print("\\n=== PHASE 1: Training Top Classifier Head ===")
history_p1 = model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_PHASE1, callbacks=cb_list)

print("\\n=== PHASE 2: Unfreezing Top Layers & Fine-Tuning ===")
with strategy.scope():
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )

history_p2 = model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS_PHASE2, callbacks=cb_list)
print(f'Training finished! Best model saved to: {os.path.abspath(MODEL_SAVE_PATH)}')
'''

notebook = {
    'cells': [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '# DeepGuard IEEE TENCON 2024 — Multi-GPU Kaggle Training Notebook\n',
                '**Hardware Accelerator**: 2x NVIDIA T4 GPUs (`T4 x2` on Kaggle)\n',
                '**Architecture**: DenseNet121 + Data Augmentation + Mixed Precision (fp16)\n',
                '**Output File**: `model.h5`'
            ]
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': nb_code.splitlines(True)
        }
    ],
    'metadata': {
        'accelerator': 'GPU_T4_X2',
        'gpuClass': 't4x2',
        'language_info': {'name': 'python'},
        'kernelspec': {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        }
    },
    'nbformat': 4,
    'nbformat_minor': 4
}

target_nb = r'C:\Users\sushi\.gemini\antigravity\scratch\deepfake-detection\deepguard\DeepGuard_Kaggle_T4x2_Training.ipynb'
with open(target_nb, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

meta = {
  "id": "divyanshuchoudhary25/deepguard-densenet121-t4x2",
  "title": "DeepGuard DenseNet121 T4x2",
  "code_file": "DeepGuard_Kaggle_T4x2_Training.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": "false",
  "enable_gpu": "true",
  "enable_tpu": "false",
  "enable_internet": "true",
  "accelerator": "gpu_t4_x2",
  "dataset_sources": [
    "manjilkarki/deepfake-and-real-images",
    "dagnelies/deepfake-faces"
  ],
  "competition_sources": [],
  "kernel_sources": []
}

target_meta = r'C:\Users\sushi\.gemini\antigravity\scratch\deepfake-detection\deepguard\kernel-metadata.json'
with open(target_meta, 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2)

print('Notebook and kernel-metadata.json successfully created!')
