# User Authentication for Streamlit App using MongoDB
# https://medium.com/@pavlo_sydorenko/simple-user-authentication-for-your-streamlit-app-using-mongodb-d6a481bbfa1

import streamlit as st
import pymongo
from pymongo.server_api import ServerApi

# Connect to the DB.
@st.experimental_singleton
def connect_db():
    client = pymongo.MongoClient(
      st.secrets["connString"], server_api=ServerApi('1'))
    db = client.get_database('dbmanagers')
    return db.users

def select_signup():
    st.session_state.form = 'signup_form'

def user_update(name):
    st.session_state.username = name

def select_signup():
    st.session_state.form = 'signup_form'
#################################################
########### Start of the program ################
#################################################

st.set_page_config(
	page_title="Lebanese Diaspora - USA",
	page_icon="Leb-Flag.png",
	layout="wide",
	initial_sidebar_state="expanded",
	menu_items={
		'Get help': 'https://github.com/tonyz80/streamLFUS/issues/1',
		'Report a bug': "https://github.com/tonyz80/streamLFUS/issues",
		'About': "# This app was designed by Tony Ziade tonyz80@gmail.com"
	})

#To hide the Streamlit hamburger (top right corner) and the “Made with Streamlit” footer:
# per https://discuss.streamlit.io/t/remove-made-with-streamlit-from-bottom-of-app/1370/5
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            #header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize Session States.
if 'username' not in st.session_state:
	st.session_state.username = ''

st.title('Pavlo Database Connection')
st.sidebar.image('LF-Logo.png',caption=None, width=100, use_column_width=False, clamp=True, channels='RGB', output_format='center')
st.sidebar.title("Login Form")

#choice = st.sidebar.selectbox('Choose Access', ['Login', 'Logout'])
username = st.sidebar.text_input('Email')
userpassword = st.sidebar.text_input('Password',type = 'password')
login=st.sidebar.button('Login')

users_db = connect_db()
st.write(users_db.find({'log' : username}))


# After 'username' and 'userpassword' are entered by the user
# Check matched in the database
if users_db.find_one({'log' : username, 'pass' : userpassword}):
	st.sidebar.success(f"You are logged in as {username}")
	if login:
		# Function selection to demonstrate how usernames are passed
		application = st.selectbox('Pick a Functon', ('Do smth', 'Do smth again'))
