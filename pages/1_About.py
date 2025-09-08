import streamlit as st

def about_us_page():
    st.set_page_config(
    page_title="Contact Us - Facebook Reels Downloader",
    page_icon="images/facebook_downloader.png",
    layout="wide"
)
    st.title("About Us - Facebook Reels Downloader")

    st.subheader("Who We Are")
    st.write(
        "We are a passionate team dedicated to making video downloading simple, "
        "fast, and reliable. Our Facebook Reels Downloader is built to help users "
        "save their favorite Reels videos in high quality directly to their devices."
    )

    st.subheader("Our Mission")
    st.write(
        "Our mission is to provide a free and user-friendly tool that allows you "
        "to download Facebook Reels instantly. Whether you want to watch offline, "
        "share with friends, or save for inspiration, our downloader ensures a smooth experience."
    )

    st.subheader("Why Choose Us")
    st.write(
        "✔ Free and unlimited downloads\n"
        "✔ High-quality HD video saving\n"
        "✔ No watermark, no hidden charges\n"
        "✔ Secure, fast, and easy to use"
    )

    st.subheader("SEO Optimized Benefits")
    st.write(
        "Our Facebook Reels Downloader is designed to be search engine optimized, "
        "ensuring that users looking to download Reels videos can easily find us online. "
        "By focusing on speed, simplicity, and quality, we help you enjoy videos offline "
        "without any hassle."
    )

    # Footer
    st.write("---")
    st.info("💡 This project is open-source and community-driven. Contributions & feedback are always welcome!")
if __name__ == "__main__":
    about_us_page()
