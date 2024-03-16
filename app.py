
import cv2
import face_recognition
import os
import streamlit as st
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfReader
import docx



# Check if Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase
    cred = credentials.Certificate("medi-bot-cce34-firebase-adminsdk-s3wca-a0a9493170.json") # Replace with your Firebase credentials
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://medi-bot-cce34-default-rtdb.firebaseio.com/'
    })

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text



# Function to upload images and extract face encodings
def upload_images():
    st.write("## Upload Images")
    uploaded_files = st.file_uploader("Choose image files", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

    known_face_encodings = []
    known_face_names = []

    if uploaded_files:
        st.write("## Uploaded Images:")
        for uploaded_file in uploaded_files:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(file_details)
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(uploaded_file.name)[0])

    return known_face_encodings, known_face_names

# Function for face recognition on video feed
def face_recognition_video(known_face_encodings, known_face_names):
    st.write("## Face Recognition Live Stream")
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Width
    cap.set(4, 480)  # Height

    while True:
        ret, frame = cap.read()

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                st.success("Image Detected!")
                st.write("Image matched! Stopping video and proceeding to the next page...")
                return

            top, right, bottom, left = face_locations[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        st.image(frame, channels="BGR")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def upload_data_to_firebase(name, age, weight, other_data, text):
    # Store the data in Firebase Realtime Database
    ref = db.reference('health_data')
    ref.push().set({
        "name": name,
        "age": age,
        "weight": weight,
        "other_data": other_data,
        "pdf_text": text
    })

def main():
    st.title("Face Recognition with Streamlit")
    known_face_encodings, known_face_names = upload_images()

    if known_face_encodings and known_face_names:
        face_recognition_video(known_face_encodings, known_face_names)
        st.write("Face detection ended. You can proceed to the next page.")
        st.write("[Proceed to next page](#user-upload-data)")

        st.markdown("""<h2 id="user-upload-data">User Upload Data</h2>""", unsafe_allow_html=True)
        st.write("This is the page for user upload data.")
        st.title("Upload Health Data PDF to Firebase Realtime Database")

        name = st.text_input("Enter Name:")
        age = st.number_input("Enter Age:", min_value=0, max_value=150)
        weight = st.number_input("Enter Weight (kg):", min_value=0.0, max_value=1000.0)
        other_data = st.text_area("Enter Other Health Data:")

        file = st.file_uploader("Upload Health Data PDF", type=["pdf"])

        if file is not None:
            temp_file = NamedTemporaryFile(delete=False)
            temp_file.write(file.getvalue())

            pdf_text = extract_text_from_pdf(temp_file.name)

            upload_data_to_firebase(name, age, weight, other_data, pdf_text)
            st.success("Health data uploaded successfully!")


if __name__ == "__main__":
    main()
 

# import cv2
# import face_recognition
# import os
# import streamlit as st
# import numpy as np
# from firebase import firebase

# # Initialize Firebase
# firebase = firebase.FirebaseApplication('https://medi-bot-cce34-default-rtdb.firebaseio.com/', None)

# # Function to upload images and extract face encodings
# def upload_images():
#     st.write("## Upload Images")
#     uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'pdf'])

#     known_face_encodings = []
#     known_face_names = []
#     uploaded_pdf_urls = []

#     if uploaded_files:
#         st.write("## Uploaded Files:")
#         for uploaded_file in uploaded_files:
#             file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
#             st.write(file_details)

#             if uploaded_file.type.startswith('image'):
#                 # Process image files
#                 file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
#                 image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#                 encoding = face_recognition.face_encodings(image)[0]
#                 known_face_encodings.append(encoding)
#                 known_face_names.append(os.path.splitext(uploaded_file.name)[0])
#             elif uploaded_file.type == 'application/pdf':
#                 # Upload PDF to Firebase
#                 pdf_url = upload_to_firebase(uploaded_file)
#                 uploaded_pdf_urls.append(pdf_url)

#     return known_face_encodings, known_face_names, uploaded_pdf_urls

# # Function to upload PDF to Firebase
# def upload_to_firebase(pdf_file):
#     # Generate a unique filename
#     filename = f"pdf_{uuid.uuid4().hex}.pdf"
    
#     # Upload the file to Firebase storage
#     firebase.storage().child(filename).put(pdf_file)
    
#     # Get the URL of the uploaded PDF
#     pdf_url = firebase.storage().child(filename).get_url(None)
    
#     return pdf_url

# # Function for face recognition on video feed
# def face_recognition_video(known_face_encodings, known_face_names):
#     st.write("## Face Recognition Live Stream")
#     cap = cv2.VideoCapture(0)
#     cap.set(3, 640)  # Width
#     cap.set(4, 480)  # Height

#     while True:
#         ret, frame = cap.read()

#         face_locations = face_recognition.face_locations(frame)
#         face_encodings = face_recognition.face_encodings(frame, face_locations)

#         for face_encoding in face_encodings:
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]
#                 st.success("Image Detected!")
#                 st.write("Image matched! Stopping video and proceeding to the next page...")
#                 return

#             top, right, bottom, left = face_locations[0]
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

#         st.image(frame, channels="BGR")

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# def main():
#     st.title("Face Recognition with Streamlit")
#     known_face_encodings, known_face_names, uploaded_pdf_urls = upload_images()

#     if known_face_encodings and known_face_names:
#         face_recognition_video(known_face_encodings, known_face_names)
#         st.write("Face detection ended. You can proceed to the next page.")
#         st.write("[Proceed to next page](#user-upload-data)")

#     st.markdown("""<h2 id="user-upload-data">User Upload Data</h2>""", unsafe_allow_html=True)
#     st.write("This is the page for user upload data.")
#     if uploaded_pdf_urls:
#         st.write("Uploaded PDF URLs:")
#         for pdf_url in uploaded_pdf_urls:
#             st.write(pdf_url)

# if __name__ == "__main__":
#     main()
