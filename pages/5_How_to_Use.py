import streamlit as st

# ✅ Browser tab title + favicon
st.set_page_config(
    page_title="How to Use - Facebook Reels Downloader",
    page_icon="images/facebook_downloader.png",
    layout="wide"
)

def how_to_use_page():
    # ✅ H1 heading
    st.title("How to Use Facebook Reels Downloader")

    st.subheader("Step 1: Copy the Reel Link")
    st.write(
        "Open Facebook on your mobile or desktop, navigate to the Reel you want to save, "
        "and copy the video link from the share option or browser address bar."
    )

    st.subheader("Step 2: Paste the Link")
    st.write(
        "Go to our Facebook Reels Downloader, paste the copied link into the input box, "
        "and make sure it’s a valid Facebook video URL."
    )

    st.subheader("Step 3: Start Download")
    st.write(
        "Click on the 'Download' button. The tool will process the link and prepare your video file."
    )

    st.subheader("Step 4: Save to Your Device")
    st.write(
        "Once the download is ready, click the provided download button to save the Reel "
        "directly to your device in HD quality."
    )

    st.subheader("Quick Summary")
    st.write(
        "Copy → Paste → Download → Save. That`s it! Our tool makes downloading "
        "Facebook Reels simple, fast, and free."
    )
        # Footer
    st.write("---")
    st.success("""**Tips:**\n
                    ✔ Make sure your internet connection is stable.\n
                    ✔ Use the latest version of your browser for smooth downloads.\n
                    ✔ Save videos responsibly and respect content ownership rights.

                """)


if __name__ == "__main__":
    how_to_use_page()
