import streamlit as st
from PIL import Image
import torch
from RealESRGAN import RealESRGAN
from io import BytesIO
import base64
import streamlit.components.v1 as components

# Function to load the model based on scale and anime toggle
def load_model(scale, anime=False):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = RealESRGAN(device, scale=scale, anime=anime)
    model_path = {
        (2, False): 'model/RealESRGAN_x2.pth',
        (4, False): 'model/RealESRGAN_x4plus.pth',
        (8, False): 'model/RealESRGAN_x8.pth',
        (4, True): 'model/RealESRGAN_x4plus_anime_6B.pth'
    }[(scale, anime)]
    model.load_weights(model_path)
    return model

def enhance_image(image, scale, anime):
    model = load_model(scale, anime=anime)
    sr_image = model.predict(image)
    
    buffer = BytesIO()
    sr_image.save(buffer, format="PNG")
    buffer.seek(0)
    return sr_image, buffer

def get_base64_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def image_comparison_slider(original_base64, enhanced_base64):
    # Define HTML and JavaScript for comparison slider
    slider_html = f"""
    <style>
    .img-comp-container {{
        position: relative;
        height: 500px;
        width: 100%;
        max-width: 800px;
        margin: auto;
    }}
    .img-comp-img {{
        position: absolute;
        width: 100%;
        height: 100%;
        overflow: hidden;
        transition: 0.4s;
    }}
    .img-comp-img img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    .img-comp-slider {{
        position: absolute;
        cursor: ew-resize;
        width: 40px;
        height: 40px;
        background-color: #2196F3;
        border-radius: 50%;
        transform: translateY(-50%);
        top: 50%;
        left: 50%;
        margin-left: -20px;
        margin-top: -20px;
        z-index: 9;
        opacity: 0.7;
        transition: 0.3s;
    }}
    .img-comp-slider:hover {{
        opacity: 1;
    }}
    .img-comp-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 0;
        overflow: hidden;
        transition: 0.4s;
        background-color: rgba(0,0,0,0.5);
    }}
    </style>
    <div class="img-comp-container">
        <div class="img-comp-img">
            <img src="data:image/png;base64,{original_base64}" />
        </div>
        <div class="img-comp-img">
            <img src="data:image/png;base64,{enhanced_base64}" />
        </div>
        <div class="img-comp-overlay"></div>
        <div class="img-comp-slider"></div>
    </div>
    <script>
    function initComparisons() {{
        var x, i;
        x = document.getElementsByClassName("img-comp-container");
        for (i = 0; i < x.length; i++) {{
            compareImages(x[i]);
        }}
        function compareImages(img) {{
            var slider, overlay, clicked = 0, w, h;
            w = img.offsetWidth;
            h = img.offsetHeight;
            slider = img.getElementsByClassName("img-comp-slider")[0];
            overlay = img.getElementsByClassName("img-comp-overlay")[0];
            img.addEventListener("mousemove", slide);
            img.addEventListener("touchmove", slide);
            img.addEventListener("mousedown", setActive);
            window.addEventListener("mouseup", removeActive);
            function slide(e) {{
                if (clicked === 0) return false;
                e.preventDefault();
                var pos = getCursorPos(e);
                if (pos.x > w) pos.x = w;
                if (pos.x < 0) pos.x = 0;
                slider.style.left = pos.x + "px";
                overlay.style.width = pos.x + "px";
            }}
            function getCursorPos(e) {{
                var a, x = 0;
                e = (e.changedTouches) ? e.changedTouches[0] : e;
                a = img.getBoundingClientRect();
                x = e.pageX - a.left;
                x = x - window.pageXOffset;
                return {{ x: x }};
            }}
            function setActive(e) {{
                clicked = 1;
                e.preventDefault();
            }}
            function removeActive() {{
                clicked = 0;
            }}
        }}
    }}
    initComparisons();
    </script>
    """
    components.html(slider_html, height=600, scrolling=True)

def main():
    st.title("Generative AI Image Restoration")

    # Image upload
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Original Image", use_column_width=True)
        
        # Anime toggle
        anime = st.checkbox("Anime Image", value=False)
        
        # Conditional scale options
        if anime:
            scale = "4x"  # Set to 4x automatically when anime is selected
        else:
            scale = st.radio("Upscaling Factor", ["2x", "4x", "8x"], index=0)
        
        scale_value = int(scale.replace('x', ''))
        
        # Enhance button
        if st.button("Restore Image"):
            enhanced_image, buffer = enhance_image(image, scale_value, anime)
            
            # Convert images to base64 for comparison slider
            original_base64 = get_base64_image(image)
            enhanced_base64 = get_base64_image(enhanced_image)
            
            # Show comparison slider
            image_comparison_slider(original_base64, enhanced_base64)
            
            # Download button
            st.download_button(
                label="Download Enhanced Image",
                data=buffer,
                file_name="enhanced_image.png",
                mime="image/png"
            )

if __name__ == "__main__":
    main()
