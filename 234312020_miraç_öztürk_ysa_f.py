# -*- coding: utf-8 -*-
"""234312020_Miraç_Öztürk_YSA_F.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18XodJw6-OFS5tTVCjv1jhz5TI35gmnbs
"""

# Hatalari gizlemek icin ilgili kod eklendi.
import warnings
warnings.filterwarnings('ignore')  # Tüm uyarilari kapatmak icin.

# İlgili kutuphaneler projeye eklendi.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.applications import DenseNet121, MobileNet
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, Callback, ModelCheckpoint
from tensorflow.keras.regularizers import l2
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import os
import random

# Hata gosterim log seviyeleri belirtildi.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 1: INFO, 2: WARNING, 3: ERROR

# Veriseti yuklemesi yapildi.
# Her kod calistirmasinde tekrar-tekrar yukleme yapmamasi icin kapatildi.

# !kaggle datasets download -d omkargurav/face-mask-dataset
# !unzip face-mask-dataset.zip -d ./face-mask-dataset

# Ilgili PATH belirtildi.
# Goruntu isleme boyutlari hazirlandi.

DATASET_PATH = "./face-mask-dataset"
image_size = (224, 224)
# batch_size = 16
# batch_size = 8
batch_size = 64

# Modelin kayit edilecegi dizin belirlendi.

SAVE_PATH = "D:/ysa/iyi_model/best_model_2.h5"
os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

#Egitim ve Dogrulama metrikleri yazdirildi.

class TrainingLogger(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        print(f"Epoch {epoch+1}/{self.params['epochs']} - accuracy: {logs.get('accuracy', 0):.4f} - loss: {logs.get('loss', 0):.4f} - val_accuracy: {logs.get('val_accuracy', 0):.4f} - val_loss: {logs.get('val_loss', 0):.4f} - learning_rate: {logs.get('lr', 0):.6f}")

# Veri On Isleme (Data Augmentation) gerceklestirildi.

train_datagen = ImageDataGenerator(
    # rescale=1.0/255,
    # rotation_range=20,
    # width_shift_range=0.3,
    # height_shift_range=0.3,
    # rotation_range=30,
    # rotation_range=40,
    # rotation_range=60,
    # width_shift_range=0.4,
    # height_shift_range=0.4,
    # shear_range=0.4,
    # shear_range=0.3,
    # shear_range=0.6,
    # brightness_range=[0.7, 1.3],
    # zoom_range=0.3,
    # shear_range=0.6,
    # brightness_range=[0.6, 1.4],
    # zoom_range=0.5,
    # zoom_range=0.2,
    # horizontal_flip=True,
    # fill_mode='nearest',
    # validation_split=0.2
    rescale=1.0/255,
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # Eğitim ve doğrulama setlerini ayırma
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='training'
)

validation_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='validation'
)

# Veri kumesi kontrolu yapildi.

if train_generator.samples == 0:
    raise ValueError("Egitim veri kumesi bos! DATASET_PATH icindeki verileri kontrol edin.")

if validation_generator.samples == 0:
    raise ValueError("Dogrulama veri kümesi bos! DATASET_PATH icindeki verileri kontrol edin.")

# Test veriseti hazirlandi.

test_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=image_size,
    batch_size=batch_size,
    class_mode='binary',
    subset='validation'
)

# Model hazirlandi.

base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(image_size[0], image_size[1], 3))

x = base_model.output
x = GlobalAveragePooling2D()(x)

# !!! Surekli Overfitting'e gittigi icin; farkli varyasyonlar denendi.
# Ilgili denen varyasyonlar; yorum olarak tutuldu.

# x = Dropout(0.6)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(x)
# x = Dropout(0.4)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.005))(x)
# x = Dropout(0.6)(x)
# x = Dropout(0.5)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
# x = Dropout(0.7)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(x)
# x = Dropout(0.6)(x)
# x = Dense(128, activation='relu', kernel_regularizer=l2(0.001))(x)
# x = Dense(64, activation='relu', kernel_regularizer=l2(0.001))(x)
# x = Dropout(0.4)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.02))(x)
# x = Dropout(0.5)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.005))(x)
# x = Dropout(0.5)(x)
# x = Dense(128, activation='relu', kernel_regularizer=l2(0.005))(x)
# x = Dense(64, activation='relu', kernel_regularizer=l2(0.005))(x)
# x = Dropout(0.5)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.03))(x)
# x = Dropout(0.6)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
# x = Dropout(0.6)(x)
# x = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(x)
# x = Dense(64, activation='relu', kernel_regularizer=l2(0.01))(x)
# x = Dropout(0.5)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
# x = Dropout(0.4)(x)
# x = Dense(256, activation='relu', kernel_regularizer=l2(0.005))(x)

x = Dropout(0.5)(x)
x = Dense(256, activation='relu', kernel_regularizer=l2(0.02))(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
x = Dropout(0.6)(x)
x = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(x)
x = Dense(64, activation='relu', kernel_regularizer=l2(0.01))(x)

predictions = Dense(1, activation='sigmoid')(x)
model = Model(inputs=base_model.input, outputs=predictions)

# Model agirliklari kayiyt edildi.

checkpoint = ModelCheckpoint(SAVE_PATH, monitor='val_loss', save_best_only=True, mode='min')

# Optimizers belirlendi.
# SGD'de test edildi; fakat basarili sonuc vermedi.

optimizers = {
    # "ADAM": Adam(learning_rate=0.001),
    # "ADAM": Adam(learning_rate=0.001),
    # "ADAM": Adam(learning_rate=0.0001),
    # "ADAM": Adam(learning_rate=0.001)
    "ADAM": Adam(learning_rate=0.000001)
}

# !!! 31. epoch sonrasinda modeil Overfitting olmaktadir.
# Sonrasinda ise hic duzelmemektedir.
# Bundan dolayi 100. epoch'a kadar gidilmistir.


# Model egitimi gerceklestirildi.

for name, optimizer in optimizers.items():
    print(f"\n{name} ile isleme baslandi.\n")
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        # factor=0.3,
        # patience=1,
        # factor=0.1,
        factor=0.2,
        patience=5,
        min_lr=1e-6
    )

    # early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)
    early_stopping = EarlyStopping(monitor='val_loss', patience=25, restore_best_weights=True)

    history = model.fit(
        train_generator,
        validation_data=validation_generator,
        # epochs=5,
        epochs=100,
        callbacks=[early_stopping, reduce_lr, checkpoint]
    )

    # Epoch basina Accuracy/Loss grafikleri cizdirildi.
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

    print(f"\n{name} ile islem bitti.\n")

# En iyi model yuklendi.
model = load_model(SAVE_PATH)

# Test verisi uzerinde tahminlemede bulunuldu.
Y_true = []
Y_pred = []
for images, labels in test_generator:
    preds = model.predict(images)
    Y_pred.extend((preds > 0.5).astype(int))
    Y_true.extend(labels.astype(int))
    if len(Y_true) >= test_generator.samples:
        break

# Test veriseti dogrulugu hesaplandi.

# !!! Overfitting oldugu icin 1-%100 degeri cikti.
# Tekrardan 36. epoch baz alinip kod calistirilamadigi icin, sonuc bu sekilde gelmektedir.

accuracy = np.mean(np.array(Y_true) == np.array(Y_pred))
print(f"Test Set Accuracy: {accuracy:.4f}")

# Confusion Matrix ve Performans Metrikleri

# !!! Overfitting.

conf_matrix = confusion_matrix(Y_true, Y_pred)
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()

print("Classification Report:")
print(classification_report(Y_true, Y_pred))

# Rastgele 5 goruntu icin tahminleme yapildi.
#Tum sonuclar; rastgele olarak dogru cikti.

indices = random.sample(range(len(Y_true)), 5)
fig, axes = plt.subplots(1, 5, figsize=(15, 5))
for i, ax in enumerate(axes):
    ax.imshow(test_generator[i][0][0])
    ax.set_title(f"Gerçek: {Y_true[indices[i]]}, Tahmin: {Y_pred[indices[i]]}")
    ax.axis("off")
plt.show()

"""### STATIK EPOCH DENEMESI"""

# !!! 36. epoch sonrasinda modeil Overfitting olmaktadir.
# Sonrasinda ise hic duzelmemektedir.
# Bundan dolayi 36. epoch'a kadar gidilmistir.


# Model egitimi gerceklestirildi.

for name, optimizer in optimizers.items():
    print(f"\n{name} ile isleme baslandi.\n")
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        # factor=0.3,
        # patience=1,
        # factor=0.1,
        factor=0.2,
        patience=5,
        min_lr=1e-6
    )

    # early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)
    early_stopping = EarlyStopping(monitor='val_loss', patience=25, restore_best_weights=True)

    history = model.fit(
        train_generator,
        validation_data=validation_generator,
        # epochs=5,
        epochs=35,
        callbacks=[early_stopping, reduce_lr, checkpoint]
    )

    # Epoch basina Accuracy/Loss grafikleri cizdirildi.
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

    print(f"\n{name} ile islem bitti.\n")

# En iyi model yuklendi.
model = load_model(SAVE_PATH)

# Test verisi uzerinde tahminlemede bulunuldu.
Y_true = []
Y_pred = []
for images, labels in test_generator:
    preds = model.predict(images)
    Y_pred.extend((preds > 0.5).astype(int))
    Y_true.extend(labels.astype(int))
    if len(Y_true) >= test_generator.samples:
        break

# 35. epoch icin tahminler.

# Rastgele 5 goruntu icin tahminleme yapildi.

indices = random.sample(range(len(Y_true)), 5)
fig, axes = plt.subplots(1, 5, figsize=(15, 5))
for i, ax in enumerate(axes):
    ax.imshow(test_generator[i][0][0])
    ax.set_title(f"Gerçek: {Y_true[indices[i]]}, Tahmin: {Y_pred[indices[i]]}")
    ax.axis("off")
plt.show()

