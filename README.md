# Rectangle Collisions

## Overview

This is a simple graphical application built using the **PyQt5** library that allows users to create rectangles, establish connections between them, and move them around within a canvas. The application supports rectangle collisions, meaning that rectangles cannot overlap.

### Key Features:

- **Create Rectangles:** Double-click in an empty area of the window to create a new rectangle.
- **Move Rectangles:** Click and drag any rectangle to reposition it.
- **Add Connections:**
  - Right-click on the first rectangle.
  - Right-click on the second rectangle to create a connection between them.
  - To deselect the first rectangle without adding a connection, click on an empty area of the window.
- **Remove Connections:** Right-click on any connection to remove it.

## Getting Started

### Prerequisites

- **Python 3.x** installed on your system.
- **PyQt5** or any other dependencies listed in `requirements.txt`.

### Installation

1. Clone or download the project to your local machine.
2. Navigate to the project directory using your terminal or command prompt.
3. Install the required dependencies using the following command:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

After installing the dependencies, you can launch the application by running the following script:

```bash
python app.py
```
