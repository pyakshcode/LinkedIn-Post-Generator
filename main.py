import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post

# Length and Language Options
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "Hinglish"]

# Main Streamlit App
def main():
    st.title("LinkedIn Post Generator")

    st.markdown("Generate engaging LinkedIn posts by selecting a topic, length, and language.")

    # Load few-shot data and get available tags
    fs = FewShotPosts()
    tags = fs.get_tags()

    # Layout: 3 dropdown columns
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_tag = st.selectbox("🎯 Select Topic", options=tags)

    with col2:
        selected_length = st.selectbox("📏 Select Length", options=length_options)

    with col3:
        selected_language = st.selectbox("🗣️ Select Language", options=language_options)

    # Generate Post Button
    if st.button("🚀 Generate Post"):
        with st.spinner("Generating your LinkedIn post..."):
            post = generate_post(selected_length, selected_language, selected_tag)
        st.markdown("### ✨ Generated Post:")
        st.write(post)

# Entry Point
if __name__ == "__main__":
    main()
