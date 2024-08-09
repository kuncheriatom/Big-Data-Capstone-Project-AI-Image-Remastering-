import streamlit as st
from PIL import Image
import torch
from RealESRGAN import RealESRGAN
from io import BytesIO
from torchvision import transforms

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

# Function to preprocess the image
def preprocess_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    return transform(image).unsqueeze(0)  # Add batch dimension

# Function to enhance the image
def enhance_image(image, scale, anime):
    model = load_model(scale, anime=anime)
    image_tensor = preprocess_image(image)
    
    try:
        sr_image = model.predict(image_tensor)
        sr_image = sr_image.squeeze(0)  # Remove batch dimension
        sr_image = transforms.ToPILImage()(sr_image)
        
        buffer = BytesIO()
        sr_image.save(buffer, format="PNG")
        buffer.seek(0)
        return sr_image, buffer
    except Exception as e:
        st.error(f"Error during model prediction: {e}")
        return None, None

def main():
    st.title("Generative AI Image Restoration")

    # Image upload
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
        except Exception as e:
            st.error(f"Error loading image: {e}")
            return
        
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
            
            if enhanced_image:
                # Show images side by side
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image, caption="Original Image", use_column_width=True)
                with col2:
                    st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)
                
                # Download button
                st.download_button(
                    label="Download Enhanced Image",
                    data=buffer,
                    file_name="enhanced_image.png",
                    mime="image/png"
                )

if __name__ == "__main__":
    main()
