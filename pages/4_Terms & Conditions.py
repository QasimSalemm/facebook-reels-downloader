import streamlit as st

# ✅ Browser tab title + favicon
st.set_page_config(
    page_title="Terms and Conditions - Facebook Reels Downloader",
    page_icon="images/facebook_downloader.png",
    layout="wide"
)

def terms_conditions_page():
    # ✅ H1 heading
    st.title("Terms and Conditions - Facebook Reels Downloader")

    st.subheader("Introduction")
    st.write(
        "Welcome to Facebook Reels Downloader. By accessing or using our service, "
        "you agree to comply with these Terms and Conditions. Please read them carefully "
        "before using our tool."
    )

    st.subheader("Use of Service")
    st.write(
        "Our downloader is provided for personal and non-commercial use only. "
        "You agree not to use the service for any unlawful purpose or in violation "
        "of applicable laws."
    )

    st.subheader("Intellectual Property Rights")
    st.write(
        "All trademarks, logos, and content belong to their respective owners. "
        "We do not claim ownership of any Facebook videos. Users are solely responsible "
        "for respecting copyright and intellectual property rights when downloading content."
    )

    st.subheader("User Responsibilities")
    st.write(
        "✔ Ensure that you have the right to download and use the videos.\n"
        "✔ Do not use the downloader for piracy, resale, or redistribution.\n"
        "✔ Accept full responsibility for how you use the downloaded content."
    )

    st.subheader("Disclaimer of Warranties")
    st.write(
        "Our service is provided 'as is' without any warranties. "
        "We do not guarantee uninterrupted, error-free, or secure downloads. "
        "Use of the downloader is at your own risk."
    )

    st.subheader("Limitation of Liability")
    st.write(
        "We are not liable for any direct, indirect, incidental, or consequential damages "
        "arising from the use of our service, including but not limited to data loss, "
        "device issues, or copyright violations."
    )

    st.subheader("Third-Party Links")
    st.write(
        "Our service may include advertisements or links to third-party sites. "
        "We are not responsible for the content, privacy practices, or policies of external websites."
    )

    st.subheader("Termination")
    st.write(
        "We reserve the right to suspend or terminate access to our service at any time "
        "without prior notice if you violate these Terms and Conditions."
    )

    st.subheader("Changes to Terms")
    st.write(
        "We may update these Terms and Conditions periodically. Updates will be posted here, "
        "and continued use of the service constitutes acceptance of the revised terms."
    )

    st.subheader("Governing Law")
    st.write(
        "These Terms and Conditions are governed by applicable international copyright "
        "and intellectual property laws."
    )

    # Footer
    st.write("---")
    st.info("📌 If you have questions about these Terms & Conditions, please contact us at qasimsaleem317@gmail.com")

if __name__ == "__main__":
    terms_conditions_page()
