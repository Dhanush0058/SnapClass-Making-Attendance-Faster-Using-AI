# SnapClass - Making Attendance Faster Using AI

<div align="center">
  <img src="https://i.ibb.co/YTYGn5qV/logo.png" alt="SnapClass Logo" width="160px">
  <h3>Smart Biometric Attendance Tracker</h3>
  <p>An AI-powered attendance tracking application built with Streamlit and Supabase, featuring multi-modal face and voice biometrics.</p>

  [![Streamlit App](https://static.streamlit.io/badge_github.svg)](https://snapclass-campus.streamlit.app)
  ![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
  ![Supabase Database](https://img.shields.io/badge/database-Supabase-green?logo=supabase)
  ![Machine Learning](https://img.shields.io/badge/AI-Face%20%26%20Voice%20Recognition-blueviolet)
</div>

---

## 📖 Overview

**SnapClass** is a modern, responsive biometric attendance system designed to simplify and accelerate the attendance-taking process. By combining **facial recognition** and **speaker identification (voice biometrics)**, SnapClass eliminates manual roll calls and sheets, providing teachers and students with a secure, instant, and contactless attendance workflow.

Teachers can manage multiple subjects, generate QR codes/join links for easy student registration, scan classroom pictures to mark present students, and record group audio to verify students by their voices. Students login securely with their FaceID, manage their subject enrollments, and track their attendance analytics.

---

## ⚡ Features

### 👨‍🏫 Teacher Portal
- **Dashboard & Course Management:** Create subjects with customizable codes, names, and sections. Easily manage student counts and total lectures.
- **Camera or Photo Upload (Face AI):** Upload a group photo of the classroom or take a snapshot. The face pipeline scans the image, detects multiple faces simultaneously, identifies enrolled students, and logs attendance.
- **Voice Attendance (Voice AI):** Record classroom audio. The pipeline splits the recording into separate speech segments, identifies who spoke based on voice patterns, and marks them present.
- **Subject Sharing:** Generate instant auto-enrollment QR codes and join-links (e.g. `?join-code=CS101`) to share with students.
- **Attendance Records:** Access detailed history of class sessions, total student counts, and absolute attendance stats.

### 🧑‍🎓 Student Portal
- **Passwordless FaceID Login:** Align your face with the camera to instantly log into your student dashboard.
- **Quick Profile Setup:** Register your face embedding and record a short audio snippet to train your voice template.
- **Interactive Dashboards:** Track your overall attendance rate across all enrolled courses.
- **Enroll / Unenroll Courses:** Search and enroll in subjects using classroom invite codes, or unenroll from courses with a single click.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend UI** | Streamlit, HTML5, Custom CSS (`Climate Crisis` & `Outfit` Fonts, Glassmorphism, Responsive base layouts) |
| **Database** | Supabase (PostgreSQL with realtime capabilities) |
| **Authentication** | FaceID Login (Dlib), Password-based logins for Teachers (hashing via `bcrypt`) |
| **Face Biometrics** | `dlib` (Frontal Face Detector), `face-recognition-models` (shape predictor & CNN v1), `scikit-learn` (Support Vector Classifier - SVC with probability scoring) |
| **Voice Biometrics** | `resemblyzer` (Utterance encoder for D-vector extraction), `librosa` (audio segmentation and wave preprocessing) |
| **Utilities** | `segno` (High-resolution QR code generator), `pandas`, `numpy`, `pillow` |

---

## 📁 Repository Structure

```directory
Snapclass/
│
├── .streamlit/
│   └── secrets.toml          # Database configurations & secrets (locally gitignored)
│
├── src/
│   ├── components/           # UI elements & Dialog overlays
│   │   ├── dialog_add_photos.py      # Camera/file uploading UI
│   │   ├── dialog_attendance_box.py  # Results list review & db save sync
│   │   ├── dialog_auto_enroll.py     # Enroll handler from shared link params
│   │   ├── dialog_create_subjects.py # Add subject modal
│   │   ├── dialog_enroll.py          # Subject registration code modal
│   │   ├── dialog_share_subjects.py  # QR code + Invite link generator
│   │   ├── dialog_voice_box.py       # Voice recorder & analyzer dialog
│   │   ├── footer.py                 # Footer UI layout
│   │   ├── header.py                 # Header brand UI layout
│   │   └── subject_card.py           # Subject statistics grid cards
│   │
│   ├── database/             # PostgreSQL clients & data hooks
│   │   ├── config.py                 # Supabase client instantiation
│   │   └── db.py                     # CRUD operations for teachers, students, logs, subjects
│   │
│   ├── pipelines/            # Core AI recognition algorithms
│   │   ├── face_pipeline.py          # Face detection (Dlib) & classifier fit (SVM)
│   │   └── voice_pipeline.py         # Voice feature extraction (Resemblyzer & Librosa)
│   │
│   ├── screens/              # Core screen templates
│   │   ├── home_screen.py            # Primary landing screen (Teacher vs Student options)
│   │   ├── student_screen.py         # Face ID verification & Student features
│   │   └── teacher_screen.py         # Login/signup & Teacher features tabs
│   │
│   └── ui/
│       └── base_layout.py            # Custom styling injects, fonts & interactive scaling
│
├── app.py                    # Main app entrypoint and routing configuration
├── requirements.txt          # Python external libraries
└── .gitignore                # Folder rules
```

---

## ⚙️ Installation & Setup

Follow these steps to set up SnapClass locally on your environment.

### Prerequisites
Make sure you have **Python 3.10 or newer** installed. You will also need C++ build tools installed on your operating system to compile `dlib` (specifically Visual Studio C++ build tools on Windows, or Xcode Command Line Tools on macOS).

### 1. Clone the Repository
```bash
git clone https://github.com/Dhanush0058/SnapClass-Making-Attendance-Faster-Using-AI.git
cd SnapClass-Making-Attendance-Faster-Using-AI
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows (cmd/PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup (Supabase)
Create a free project on [Supabase](https://supabase.com). Execute the following schema inside your SQL Editor to set up the relational tables:

```sql
-- 1. Create Teachers Table
create table teachers (
    teacher_id bigint generated always as identity primary key,
    username text unique not null,
    password text not null,
    name text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Create Students Table
create table students (
    student_id bigint generated always as identity primary key,
    name text not null,
    face_embedding double precision[], -- stores the 128D face signature array
    voice_embedding double precision[], -- stores the 256D voice signature array
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Create Subjects Table
create table subjects (
    subject_id bigint generated always as identity primary key,
    subject_code text unique not null,
    name text not null,
    section text not null,
    teacher_id bigint references teachers(teacher_id) on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. Create Subject Enrollment Table (Many-to-Many relationship)
create table subject_students (
    id bigint generated always as identity primary key,
    student_id bigint references students(student_id) on delete cascade not null,
    subject_id bigint references subjects(subject_id) on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(student_id, subject_id)
);

-- 5. Create Attendance Logs Table
create table attendance_logs (
    log_id bigint generated always as identity primary key,
    student_id bigint references students(student_id) on delete cascade not null,
    subject_id bigint references subjects(subject_id) on delete cascade not null,
    timestamp timestamp not null,
    is_present boolean not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

### 5. Setup Secrets Configuration
Create a `.secrets.toml` file inside the `.streamlit/` directory at the project root to authenticate with your database:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

### 6. Run the Application
Start the Streamlit development server locally:
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser to interact with the application.

---

## 🧠 Biometric Pipelines Behind the Scenes

### 👤 Facial Recognition Pipeline
1. **Detection:** When a classroom picture or student login image is processed, the system triggers `dlib`'s Frontal Face Detector.
2. **Feature Extraction:** A pre-trained CNN predictor models facial landmarks and extracts a **128-dimensional embedding** vector representing the distinct features of each face.
3. **Classification:**
   - On student registration, the face vectors are stored inside Supabase.
   - During the analysis phase, a **Support Vector Machine (SVC)** classifier from `scikit-learn` is trained on-the-fly with all student face embeddings as training classes.
   - For multi-face detections, the classifier predicts identity labels and measures Euclidean distances (L2 Norm) to screen out unrecognized individuals (threshold: `distance <= 0.6`).

### 🎙️ Voice Biometrics Pipeline
1. **Utterance Processing:** Student voice profiles are recorded via Streamlit's audio input. The signal is read and normalized using `librosa` at a sample rate of `16,000 Hz`.
2. **Embedding Generation:** The normalized wav data is passed to `resemblyzer`'s deep-learning model to generate a **D-vector** summarizing the speaker's vocal characteristics.
3. **Audio Segmentation:** In classroom mode, the system splits long recordings into active speech segments based on dB thresholds (`top_db=30`) using `librosa.effects.split`.
4. **Speaker Matching:** Each speech segment is analyzed, and cosine similarity matches are calculated against the target subject's registered student embeddings. High-confidence matches above the similarity threshold (`>= 0.65`) are automatically recorded as present.

---

## 🎨 Styling and UX Design
SnapClass uses a custom glassmorphism and styled dashboard architecture. Styling accents are injected dynamically at runtime via `src/ui/base_layout.py`:
- Injects fonts directly from Google Fonts: **Climate Crisis** (a bold, punchy display font for headers) and **Outfit** (a clean geometric font for inputs and content).
- Implements Discord-like design language: vibrant blue background (`#5865F2`) on home screen, soft lavender/blue base canvas (`#E0E3FF`) for dashboards, and hot pink (`#EB459E`) for warnings/secondary button actions.
- Incorporates micro-animations like scaling triggers (`transform: scale(1.05)`) on hover events.

---

## 🤝 Contribution
Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Created with ❤️ by **Dhanush**.
