import streamlit as st

# ✅ Browser tab title + favicon
st.set_page_config(
    page_title="Privacy Policy - Facebook Reels Downloader",
    page_icon="images/facebook_downloader.png",
    layout="wide"
)

def privacy_policy_page():
    # ✅ H1 heading
    st.title("Privacy Policy - Facebook Reels Downloader")

    st.subheader("Introduction")
    st.write(
        "At Facebook Reels Downloader, your privacy is our priority. "
        "This Privacy Policy explains how we handle your information when you use our service. "
        "By using our tool, you agree to the practices outlined below."
    )

    st.subheader("Information We Do Not Collect")
    st.write(
        "We respect your privacy. We do not require account registration, "
        "and we do not collect personal data such as your name, email address, or browsing history."
    )

    st.subheader("How Our Tool Works")
    st.write(
        "Our downloader processes video links provided by you and generates downloadable files. "
        "The videos are fetched directly from Facebook’s servers and are not stored on our servers."
    )

    st.subheader("Cookies & Analytics")
    st.write(
        "We may use cookies to improve site performance and user experience. "
        "These cookies do not contain personally identifiable information. "
        "Analytics tools may be used to understand general traffic trends."
    )

    st.subheader("Third-Party Services")
    st.write(
        "Our service may display third-party advertisements or links. "
        "We are not responsible for the privacy practices of external websites."
    )

    st.subheader("Data Security")
    st.write(
        "We take reasonable measures to ensure the security of our platform. "
        "Since we do not store your personal information, risks are minimal. "
        "However, no online service can be 100% secure."
    )

    st.subheader("Children`s Privacy")
    st.write(
        "Our service is not directed toward children under 13. "
        "We do not knowingly collect data from minors."
    )

    st.subheader("Policy Updates")
    st.write(
        "We may update this Privacy Policy from time to time. "
        "Changes will be posted here with the updated effective date."
    )

    st.write("---")
    st.info("📌 If you have any questions about this Privacy Policy, please contact us at qasimsaleem317@gmail.com")

if __name__ == "__main__":
    privacy_policy_page()
