import streamlit as st
from src.ui.base_layout import style_background_dashboard,style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
import numpy as np
import pandas as pd
from datetime import datetime
from src.database.config import supabase
from src.pipelines.face_pipeline import predict_attendence
from src.database.db import create_teacher , check_teacher_exists,teacher_login,get_teacher_subjects,get_attendance_for_teacher
from src.components.dialog_create_subjects import create_subject_dialog
from src.components.dialog_share_subjects import share_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_add_photos import add_photos_dialog
from src.components.dialog_attendance_box import attendance_dialog_box
from src.components.dialog_voice_box import voice_attendance_dialog
def teacher_screen():
    
    style_background_dashboard()
    style_base_layout()

    
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_Login_Type' not in st.session_state or st.session_state.teacher_Login_Type == 'login':
        teacher_screen_login()
    elif st.session_state.teacher_Login_Type == "register":
        teacher_screen_register()

    


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
     
    
    c1 , c2 = st.columns(2, vertical_alignment='center' , gap = 'xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """ , text_alignment=  'center')
        if st.button("Logout", type = 'secondary', key = 'loginbackbtn',shortcut = 'control+ backspace'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()

    st.space('small')


    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1 , tab2 , tab3 = st.columns(3)

    with tab1:
        type1 = 'primary' if st.session_state.current_teacher_tab == 'take_attendance' else 'tertiary'
        if st.button("Take Attendance",type = type1,width ='stretch' , icon = ':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = 'primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary'
        if st.button('Manage Subjects',type = type2,width ='stretch' , icon = ':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab =='attendance_records' else 'tertiary'
        if st.button('Attendance Records',type = type3,width ='stretch' , icon = ':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendance':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'attendance_records':
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("You haven't created any subjects yets !Please create one")
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1 , col2 = st.columns([3,1],vertical_alignment= 'bottom')
    with col1:
        selected_subject_label = st.selectbox("Select Subject",options = list(subject_options.keys()))

    with col2:
        if st.button("Add Photos",type ='primary', icon = ':material/photo_library:',width = 'stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header("Added Photos")
        gallery_cols = st.columns(4)

        for idx , img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img , width = 'stretch' ,caption = f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1 , c2 , c3 = st.columns(3)

    with c1:
        if st.button("Clear all images", width = 'stretch',type = 'tertiary',icon = ':material/delete:',disabled =not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        
        if st.button("Run face analysis", width = 'stretch',type = 'secondary',icon = ':material/analytics:',disabled = not has_photos):
            with st.spinner("Deep scanning classroom photos..."):
                all_detected_ids = {}
                for idx , img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected ,_,_ = predict_attendence(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            
                            all_detected_ids.setdefault(student_id,[]).append(f"Photo {idx+1}")
                
                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id).execute()
                enrolled_students = enrolled_res.data
                
                if not enrolled_students:
                    st.warning("No students enrolled in this course")
                else:
                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']) , [])

                        is_present = len(sources)>0
                        results.append({
                            'Name' : student['name'],
                            'ID' :   student['student_id'],
                            'Source': ".".join(sources) if is_present else "-",
                            'Status' : '✅ Present' if is_present else "❌ Absent"                                         
                        })

                        attendance_to_log.append({
                            "student_id": student["student_id"],
                            'subject_id' :selected_subject_id,
                            'timestamp':current_timestamp,
                            'is_present' : bool(is_present)
                        })

                attendance_dialog_box(pd.DataFrame(results),attendance_to_log)
    with c3:   
        if st.button("Use voice Attendance",width = 'stretch',type = 'primary', icon =":material/mic:"):
            voice_attendance_dialog(selected_subject_id)



def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1 , col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button('Create New Subject', width = 'stretch'):
            create_subject_dialog(teacher_id)
    #List all subjects
    subjects =  get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = {
                ("👥","Students" ,sub['total_students']),
                ('🏛️' ,'Classes' , sub['total_classes']),

            }
        def share_btn():
            if st.button(f"Share Code: {sub['name']}",key=f'share_{sub['subject_code']}',icon =":material/share:"):
                share_subject_dialog(sub['name'] , sub['subject_code'])
            st.space('medium')

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats = stats,
            footer_callback = share_btn
        )       
    else:
        st.info("No Subjects found ,Create One")
    
def teacher_tab_attendance_records():
    st.header("Attendance records")

    teacher_id = st.session_state.teacher_data['teacher_id']

    record = get_attendance_for_teacher(teacher_id)

    if not record:
        return
    
    data = []

    for r in record:
        ts= r.get('timestamp')
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject_Code": r['subjects']['subject_code'],
            "is_present":bool(r.get('is_present',False))
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject_Code'])
        .agg(
            Present_Count =  ('is_present','sum'),
            Total_Count = ('is_present' ,'count')
        ).reset_index()
    )
    summary['Attendance_Stats'] = (
        "✅ " +summary['Present_Count'].astype(str) + " /"
        +summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = (summary.sort_values(by = 'ts_group',ascending  =False)
                    [["Time",'Subject','Subject_Code','Attendance_Stats']]

                    )

    st.dataframe(display_df , width = 'stretch',hide_index = True )


        
def login_teacher(username , pwd):
    if not username or not pwd:
        return False
    
    teacher = teacher_login(username , pwd)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
def register_teacher(teacher_name , teacher_username,teacher_password,teacher_confirm_password):
    if not teacher_username or not teacher_name or not teacher_password:
        return False , "All Fields are required to fill!"
    if check_teacher_exists(teacher_username):
        return False , "Username already taken"
    if teacher_password != teacher_confirm_password:
        return False ," Password did not match!"
    try:
        create_teacher(teacher_username , teacher_password , teacher_name)
        return True , "Successfully Registered"
    except Exception as e:
        return False , "Unexpected Error"


def teacher_screen_login():
    c1 , c2 = st.columns(2, vertical_alignment='center' , gap = 'xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go Back To Home", type = 'secondary', key = 'loginbackbtn',shortcut = 'control + backspace'):
            st.session_state['Login_Type'] = None
            st.rerun()

    st.header("Login using password", text_alignment = 'center')
    st.space('large')

    teacher_username = st.text_input("Enter username" , placeholder = 'name')

    teacher_password = st.text_input("Enter password",type = 'password')
    
    st.divider()

    btc1 , btc2 = st.columns(2)
    with btc1:
        if st.button('Login' , icon = ':material/passkey:',shortcut = 'control + enter',width = 'stretch'):
            if login_teacher(teacher_username , teacher_password):
                st.toast("Welcome back!",icon ="🎉")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("Login Failed!")
    with btc2:
        if st.button('Register', type = 'primary' ,icon = ':material/passkey:',width = 'stretch'):
            st.session_state.teacher_Login_Type = 'register'
    footer_dashboard()


def teacher_screen_register():
    c1 , c2 = st.columns(2, vertical_alignment='center' , gap = 'xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go Back To Home", type = 'secondary', key = 'loginbackbtn',shortcut = 'control + backspace'):
            st.session_state['Login_Type'] = None
            st.rerun()

    
    st.header("Register your Teacher profile", text_alignment = 'center')
    st.space('large')

    teacher_username = st.text_input("Enter username" , placeholder = 'username')
    teacher_name = st.text_input("Enter name" , placeholder = 'name')

    
    teacher_password = st.text_input("Enter password",type = 'password')
    teacher_confirm_password = st.text_input("Confirm password",type = 'password')
    
    st.divider()

    btc1 , btc2 = st.columns(2)
    with btc1:
        if st.button('Register' , icon = ':material/passkey:',shortcut = 'control + enter',width = 'stretch'):
            success, message = register_teacher(teacher_name , teacher_username,teacher_password,teacher_confirm_password)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_Login_Type = "login"
                st.rerun()
            else:
                st.error(message)

    with btc2:
        if st.button('Login', type = 'primary' ,icon = ':material/passkey:',width = 'stretch'):
            st.session_state.teacher_Login_Type = 'login'
    footer_dashboard()

    # st.header("Teacher Screen")


