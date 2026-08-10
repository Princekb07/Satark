#include <Arduino_LED_Matrix.h>
#include "heart_frames.h"

Arduino_LED_Matrix matrix;

void setup() {
    matrix.begin();
    matrix.clear();
    matrix.loadFrame(HeartStatic);
}

void loop() {
}
