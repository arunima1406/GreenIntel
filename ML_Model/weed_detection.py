import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
from keras.layers import Dropout

IMAGE_DIR = r"C:\Users\Administrator\Desktop\vscode\ElectroHack\agri_data\images"
LABEL_DIR = r"C:\Users\Administrator\Desktop\vscode\ElectroHack\agri_data\labels"
NON_WEED_DIR = r"C:\Users\Administrator\Downloads\archive (1)\data"
# Combine weed and non-weed data

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

def yolo_to_ssd(yolo_box, img_width, img_height):
    x_center, y_center, width, height = yolo_box
    x_min = int((x_center - width / 2) * img_width)
    y_min = int((y_center - height / 2) * img_height)
    x_max = int((x_center + width / 2) * img_width)
    y_max = int((y_center + height / 2) * img_height)
    return [x_min, y_min, x_max, y_max]

def check_labels(label_dir):
    class_counts = {}
    for file in os.listdir(label_dir):
        if file.endswith(".txt"):
            with open(os.path.join(label_dir, file), 'r') as f:
                for line in f:
                    class_id = line.strip().split()[0]
                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
    print("Class Distribution in Labels:", class_counts)
    return class_counts

def load_and_preprocess_images(image_dir, label_dir):
    images, labels = [], []
    print(f"Loading images from: {image_dir}")
    print(f"Loading labels from: {label_dir}")

    if not os.path.exists(image_dir):
        print(f"Error: Image directory does not exist: {image_dir}")
        return np.array([]), np.array([])

    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg'))]
    print(f"Found {len(image_files)} image files")

    for img_file in image_files:
        img_path = os.path.join(image_dir, img_file)
        label_path = os.path.join(label_dir, img_file.replace('.jpg', '.txt').replace('.jpeg', '.txt'))

        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to load image: {img_path}")
            continue

        img_height, img_width = img.shape[:2]
        img = cv2.resize(img, (224, 224))  
        img = preprocess_input(img)

        boxes = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_id, *box = map(float, line.strip().split())
                    boxes.append(yolo_to_ssd(box, img_width, img_height))
        else:
            print(f"Label file not found: {label_path}")

        labels.append(1 if any(box[0] != 0 for box in boxes) else 0)  
        images.append(img)

    print(f"Successfully loaded {len(images)} images")
    return np.array(images), to_categorical(labels, num_classes=2)

def create_mobilenet_ssd(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Unfreeze some top layers
    for layer in base_model.layers[-20:]:
        layer.trainable = True
    # Unfreeze some top layers
    
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(x)
    x = Dropout(0.5)(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

def train_with_kfold(X, y, n_splits=5):
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_no = 1
    acc_per_fold = []
    loss_per_fold = []

    for train, test in kfold.split(X, y):
        model = create_mobilenet_ssd(num_classes=2)
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        
        history = model.fit(
            X[train], y[train],
            epochs=10,
            batch_size=32,
            validation_data=(X[test], y[test]),
            verbose=0
        )
        
        scores = model.evaluate(X[test], y[test], verbose=0)
        print(f'Score for fold {fold_no}: {model.metrics_names[0]} of {scores[0]}; {model.metrics_names[1]} of {scores[1]*100}%')
        acc_per_fold.append(scores[1] * 100)
        loss_per_fold.append(scores[0])
        
        fold_no += 1

    print('------------------------------------------------------------------------')
    print('Score per fold')
    for i in range(0, len(acc_per_fold)):
        print(f'> Fold {i+1} - Loss: {loss_per_fold[i]} - Accuracy: {acc_per_fold[i]}%')
    print('------------------------------------------------------------------------')
    print('Average scores for all folds:')
    print(f'> Accuracy: {np.mean(acc_per_fold)} (+- {np.std(acc_per_fold)})')
    print(f'> Loss: {np.mean(loss_per_fold)}')
    print('------------------------------------------------------------------------')

    return model  # Return the last trained model

def test_on_various_images(model, test_dir):
    for img_file in os.listdir(test_dir):
        img_path = os.path.join(test_dir, img_file)
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (224, 224))
            img = preprocess_input(img)
            prediction = model.predict(np.expand_dims(img, axis=0))
            class_pred = "Weed" if prediction[0][1] > 0.5 else "Not Weed"
            confidence = prediction[0][1] if class_pred == "Weed" else 1 - prediction[0][1]
            print(f"Image: {img_file}, Prediction: {class_pred}, Confidence: {confidence:.2f}")

def load_non_weed_images(non_weed_dir, num_images=1300):
    non_weed_images = []
    non_weed_labels = []
    
    for img_file in os.listdir(non_weed_dir)[:num_images]:
        img_path = os.path.join(non_weed_dir, img_file)
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (224, 224))
            img = preprocess_input(img)
            non_weed_images.append(img)
            non_weed_labels.append(0)  # 0 for non-weed
    
    return np.array(non_weed_images), to_categorical(non_weed_labels, num_classes=2)



def process_and_detect_weeds():
    class_counts = check_labels(LABEL_DIR)
    if len(class_counts) < 2:
        print("⚠ Warning: Dataset may be imbalanced or incorrectly labeled.")

    X, y = load_and_preprocess_images(IMAGE_DIR, LABEL_DIR)

    non_weed_X, non_weed_y = load_non_weed_images(NON_WEED_DIR, num_images=1300)
    X = np.concatenate([X, non_weed_X])
    y = np.concatenate([y, non_weed_y])

    if X.shape[0] == 0 or y.shape[0] == 0:
        print("Error: No images were loaded. Check dataset.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest',
        brightness_range=[0.7, 1.3]
    )

    model = create_mobilenet_ssd(num_classes=2)
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=32),
        epochs=5,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping],
        verbose=1
    )

    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"🔹 Test Accuracy: {test_accuracy*100:.2f}%")

    if X_test.shape[0] > 0:
        sample_img = X_test[0]
        predictions = model.predict(np.expand_dims(sample_img, axis=0))
        detected_class = np.argmax(predictions[0])
        print(f"Detected Class: {'Weed' if detected_class == 1 else 'No Weed'}")
    else:
        print("No test images available for detection.")

    model.save("WeedDetectionModel.h5")
    print("Model saved as")

if _name_ == "_main_":
    process_and_detect_weeds()