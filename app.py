import streamlit as st
from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

def main():
    if 'Login_Type' not in st.session_state:
        st.session_state['Login_Type'] = None
    match st.session_state['Login_Type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()


main() 