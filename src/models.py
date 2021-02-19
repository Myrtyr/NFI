from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Dense, Flatten, Dropout, Conv1D, Conv2D, MaxPool2D, MaxPool1D, \
    MaxPooling2D, UpSampling2D, concatenate
from tensorflow.keras.optimizers import Adam


def dense_model(n_classes):
    model = Sequential()
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(16, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(n_classes, activation='sigmoid'))
    return model


def conv_model(n_labels):
    # should probably add more filters, but not sure how to choose it
    filter_s = 3
    kernelsize = 3
    poolsize = (3, 1)
    # can also flatten within layers
    model = Sequential()
    model.add(Conv1D(6, kernelsize, activation='relu'))
    model.add(Conv1D(6, kernelsize, activation='relu'))
    model.add(MaxPool2D(poolsize))
    model.add(Conv1D(6, kernelsize, activation='relu'))
    model.add(Conv1D(6, kernelsize, activation='relu'))
    model.add(MaxPool2D(poolsize))
    model.add(Flatten())
    model.add(Dense(50, activation='relu'))
    model.add(Dropout(rate=0.5))
    model.add(Dense(20, activation='relu'))
    model.add(Dense(n_labels, activation='sigmoid'))
    return model


def model_for_example(n_features, n_classes):
    model = Sequential()
    model.add(Dense(32, activation='relu', input_dim=n_features))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(n_classes, activation='sigmoid'))
    return model


def unet_from_aml(input_size=(256, 256, 3)):
    inputs = Input(input_size)

    # Convolution 1
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(inputs)
    conv1 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv1)
    # Pooling 1
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    # Convolution 2
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv2)
    # Pooling 2
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    # Convolution 3
    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(pool2)

    conv3 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv3)
    # Pooling 3
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    # Convolution 3
    conv4 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(pool3)

    conv4 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv4)
    # Dropout
    drop4 = Dropout(0.5)(conv4)

    # Pooling 4
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    # Convolution 5
    conv5 = Conv2D(1024, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(pool4)

    conv5 = Conv2D(1024, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv5)
    # Dropout
    drop5 = Dropout(0.5)(conv5)

    # Upward Convolution 6
    up6 = Conv2D(512, 2, activation='relu', padding='same',
                 kernel_initializer='he_normal'
                 )(UpSampling2D(size=(2, 2))(drop5))

    # Here we copy the input from the upward convolution and contraction path
    merge6 = concatenate([drop4, up6])

    conv6 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(merge6)

    conv6 = Conv2D(512, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv6)

    # Upward Convolution 7
    up7 = Conv2D(256, 2, activation='relu', padding='same',
                 kernel_initializer='he_normal'
                 )(UpSampling2D(size=(2, 2))(conv6))

    # Here we copy the input from the upward convolution and contraction path
    merge7 = concatenate([conv3, up7])

    conv7 = Conv2D(256, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(merge7)

    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal'
                   )(conv7)

    # Upward Convolution 8
    up8 = Conv2D(128, 2, activation='relu', padding='same',
                 kernel_initializer='he_normal'
                 )(UpSampling2D(size=(2, 2))(conv7))

    # Here we copy the input from the upward convolution and contraction path
    merge8 = concatenate([conv2, up8])

    conv8 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(merge8)

    conv8 = Conv2D(128, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv8)
    # Upward Convolution 9
    up9 = Conv2D(64, 2, activation='relu', padding='same',
                 kernel_initializer='he_normal'
                 )(UpSampling2D(size=(2, 2))(conv8))

    # Here we copy the input from the upward convolution and contraction path
    merge9 = concatenate([conv1, up9])

    conv9 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(merge9)

    conv9 = Conv2D(64, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv9)

    conv9 = Conv2D(2, 3, activation='relu', padding='same',
                   kernel_initializer='he_normal'
                   )(conv9)

    conv10 = Conv2D(1, 1, activation='sigmoid')(conv9)

    model = Model(inputs=inputs, outputs=conv10)

    model.compile(optimizer=Adam(lr=1e-3), loss='binary_crossentropy', metrics=['accuracy'])

    return model


def crnn():
    pass
