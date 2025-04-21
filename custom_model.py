import os
import random
import string
from captcha.image import ImageCaptcha
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, backend as K

# Constants
CHARACTERS = string.ascii_lowercase  # Changed to lowercase letters only
CAPTCHA_LENGTH = 6  # Length matches "pulgfm"
IMG_WIDTH = 215  # Adjusted to match the image proportions
IMG_HEIGHT = 80
CHAR_TO_LABEL = {char: idx for idx, char in enumerate(CHARACTERS)}
LABEL_TO_CHAR = {idx: char for char, idx in CHAR_TO_LABEL.items()}
DATASET_DIR = "captcha_dataset"

# 1. Generate CAPTCHA images
def generate_captchas(n=100):
    os.makedirs(DATASET_DIR, exist_ok=True)
    captcha_gen = ImageCaptcha(
        width=IMG_WIDTH, 
        height=IMG_HEIGHT,
        fonts=['arial.ttf'],
        font_sizes=(42,)
    )
    
    for _ in range(n):
        text = ''.join(random.choices(CHARACTERS, k=CAPTCHA_LENGTH))
        img = captcha_gen.generate_image(text)
        img = img.convert('L')
        # Convert to uint8 array before saving
        img_array = np.array(img) * 0.8 + 30
        img_array = img_array.clip(0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        img.save(os.path.join(DATASET_DIR, f"{text}.png"))

# 2. Load and preprocess dataset
def load_dataset():
    X = []
    y = []
    input_len = []
    label_len = []
    
    # Load images from dataset_1 directory
    dataset_path = "dataset_1"
    for image_file in os.listdir(dataset_path):
        if image_file.endswith('.png'):
            # Get text from filename
            text = image_file.split('_')[1].split('.')[0]
            
            # Load and preprocess image
            img = Image.open(os.path.join(dataset_path, image_file)).convert('L')
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img = np.array(img) / 255.0
            
            # Convert text to label sequence
            label = [CHAR_TO_LABEL[c] for c in text]
            
            X.append(img)
            y.append(label)
            input_len.append(IMG_WIDTH // 8)  # Based on CNN structure
            label_len.append(len(text))
    
    X = np.array(X)
    X = np.expand_dims(X, axis=-1)
    return X, y, np.array(input_len), np.array(label_len)

# 3. CTC Loss
def ctc_lambda_func(args):
    y_pred, labels, input_length, label_length = args
    return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

# 4. Model
def build_model():
    input_img = layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 1), name="image")
    labels = layers.Input(name="label", shape=(CAPTCHA_LENGTH,), dtype="int32")
    input_length = layers.Input(name="input_length", shape=(1,), dtype="int32")
    label_length = layers.Input(name="label_length", shape=(1,), dtype="int32")

    x = layers.Conv2D(32, (3,3), activation='relu', padding='same')(input_img)
    x = layers.MaxPooling2D((2,2))(x)
    x = layers.Conv2D(64, (3,3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2,2))(x)

    new_shape = (IMG_WIDTH // 4, (IMG_HEIGHT // 4) * 64)
    x = layers.Reshape(target_shape=new_shape)(x)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)
    x = layers.Dense(len(CHARACTERS)+1, activation='softmax')(x)

    loss_out = layers.Lambda(ctc_lambda_func, output_shape=(1,), name="ctc")(
        [x, labels, input_length, label_length]
    )

    model = models.Model(inputs=[input_img, labels, input_length, label_length], outputs=loss_out)
    pred_model = models.Model(inputs=input_img, outputs=x)
    return model, pred_model

# 5. Train the model
def train():
    X, y, input_len, label_len = load_dataset()
    
    y_padded = tf.keras.preprocessing.sequence.pad_sequences(y, maxlen=16, padding='post', value=-1)
    
    model, pred_model = build_model()
    model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer='adam')
    
    # Added training monitoring
    history = model.fit(
        x={
            'image': X,
            'label': y_padded,
            'input_length': input_len,
            'label_length': label_len
        },
        y=np.zeros(len(X)),
        epochs=100,  # Increased epochs for better learning
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    # Print training results
    print("\nTraining History:")
    for epoch, loss in enumerate(history.history['loss']):
        print(f"Epoch {epoch + 1}: Loss = {loss:.4f}")
    
    pred_model.save("captcha_reader.h5")
    print("✅ Model saved as captcha_reader.h5")

if __name__ == "__main__":
    train()

