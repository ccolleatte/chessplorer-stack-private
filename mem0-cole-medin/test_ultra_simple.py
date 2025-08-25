import streamlit as st

st.title('🎯 Test Ultra Simple')
st.write('Si vous voyez ceci, Streamlit fonctionne parfaitement !')

name = st.text_input('Votre nom')
if name:
    st.write(f'Bonjour {name} !')

if st.button('Test Button'):
    st.success('✅ Button fonctionne !')

st.write('---')
st.write('🔧 Variables d\'environnement :')
import os
st.write(f'OPENAI_API_KEY: {"✅" if os.getenv("OPENAI_API_KEY") else "❌"}')
st.write(f'SUPABASE_URL: {os.getenv("SUPABASE_URL", "Non définie")}')
