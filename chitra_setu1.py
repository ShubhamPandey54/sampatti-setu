import cv2
import numpy as np
from PIL import Image
from rembg import remove
import io

import torch
import torch.nn.functional as F
from torchvision import transforms



# DEVICE


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)



# LOAD DINOV2


print("Loading DINOv2...")

dino_model = torch.hub.load(
    "facebookresearch/dinov2",
    "dinov2_vits14"
)

dino_model = dino_model.to(device)
dino_model.eval()

print("DINOv2 loaded successfully.")



# DINOV2 IMAGE TRANSFORMATION


dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])



# 1. BACKGROUND REMOVAL


def remove_background(image_path):

    """
    Removes the background from an image.

    Returns:
        PIL RGBA image
    """

    with open(image_path, "rb") as file:
        input_data = file.read()

    output_data = remove(input_data)

    image = Image.open(
        io.BytesIO(output_data)
    ).convert("RGBA")

    return image



# 2. PREPARE IMAGE FOR SIFT


def prepare_image(image_path):

    """
    Removes the background and performs
    lighting normalization.
    """

    # Remove background
    image = remove_background(
        image_path
    )

    # Create white background
    background = Image.new(
        "RGBA",
        image.size,
        (255, 255, 255, 255)
    )

    background.alpha_composite(
        image
    )

    rgb = background.convert("RGB")

    # PIL -> NumPy
    img = np.array(rgb)

    # RGB -> BGR
    img = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2BGR
    )

    
    # Resize
    

    height, width = img.shape[:2]

    max_dimension = 1200

    scale = min(
        max_dimension / width,
        max_dimension / height,
        1
    )

    if scale < 1:

        img = cv2.resize(
            img,
            (
                int(width * scale),
                int(height * scale)
            ),
            interpolation=cv2.INTER_AREA
        )

    
    # Grayscale
    

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    
    # Lighting normalization
    

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    normalized = clahe.apply(
        gray
    )

    return normalized



# 3. EXTRACT SIFT FEATURES


def extract_sift(image):

    """
    Finds distinctive local features such as:

    - scratches
    - edges
    - logos
    - texture
    - dents
    - patterns
    """

    sift = cv2.SIFT_create(
        nfeatures=3000
    )

    keypoints, descriptors = (
        sift.detectAndCompute(
            image,
            None
        )
    )

    return keypoints, descriptors



# 4. SIFT MATCHING


def sift_match(
    image1,
    image2
):

    kp1, des1 = extract_sift(
        image1
    )

    kp2, des2 = extract_sift(
        image2
    )

    if des1 is None or des2 is None:

        return [], (kp1, kp2)

    # BFMatcher
    matcher = cv2.BFMatcher(
        cv2.NORM_L2
    )

    matches = matcher.knnMatch(
        des1,
        des2,
        k=2
    )

    good_matches = []

    # Lowe ratio test
    for m, n in matches:

        if m.distance < 0.75 * n.distance:

            good_matches.append(m)

    return good_matches, (kp1, kp2)


# ============================================================
# 5. RANSAC GEOMETRIC VERIFICATION
# ============================================================

def verify_geometry(
    good_matches,
    keypoints
):

    """
    Checks whether matched points have
    a consistent geometric relationship.
    """

    kp1, kp2 = keypoints

    if len(good_matches) < 4:

        return 0

    src_points = np.float32([
        kp1[m.queryIdx].pt
        for m in good_matches
    ]).reshape(
        -1,
        1,
        2
    )

    dst_points = np.float32([
        kp2[m.trainIdx].pt
        for m in good_matches
    ]).reshape(
        -1,
        1,
        2
    )

    matrix, mask = cv2.findHomography(
        src_points,
        dst_points,
        cv2.RANSAC,
        5.0
    )

    if mask is None:

        return 0

    inliers = int(
        mask.sum()
    )

    return inliers


# ============================================================
# 6. SIFT SCORE
# ============================================================

def calculate_sift_score(
    good_matches,
    inliers
):

    if len(good_matches) == 0:

        return 0

    # Geometric consistency
    geometry_score = (
        inliers /
        len(good_matches)
    )

    # Number of matching features
    feature_score = min(
        len(good_matches) / 50,
        1
    )

    score = (
        0.6 * geometry_score +
        0.4 * feature_score
    )

    return score * 100


# ============================================================
# 7. DINOV2 EMBEDDING
# ============================================================

def get_dino_embedding(
    image_path
):

    """
    Converts an image into a DINOv2
    feature vector.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    image = dino_transform(
        image
    )

    # Add batch dimension
    image = image.unsqueeze(
        0
    )

    image = image.to(
        device
    )

    with torch.no_grad():

        embedding = dino_model(
            image
        )

    # Normalize
    embedding = F.normalize(
        embedding,
        p=2,
        dim=1
    )

    return embedding


# ============================================================
# 8. DINOV2 COMPARISON
# ============================================================

def compare_dino(
    image1_path,
    image2_path
):

    embedding1 = get_dino_embedding(
        image1_path
    )

    embedding2 = get_dino_embedding(
        image2_path
    )

    similarity = F.cosine_similarity(
        embedding1,
        embedding2
    )

    return similarity.item()


# ============================================================
# 9. COMPLETE IMAGE COMPARISON
# ============================================================

def compare_images(
    image1_path,
    image2_path
):

    print("\n================================")
    print("STARTING IMAGE COMPARISON")
    print("================================")

    # --------------------------------------------------------
    # SIFT PROCESSING
    # --------------------------------------------------------

    print("\n[1/4] Removing background...")

    image1 = prepare_image(
        image1_path
    )

    image2 = prepare_image(
        image2_path
    )

    print(
        "[2/4] Extracting SIFT features..."
    )

    good_matches, keypoints = sift_match(
        image1,
        image2
    )

    print(
        "Good matches:",
        len(good_matches)
    )

    
    # RANSAC
    

    print(
        "[3/4] Performing RANSAC verification..."
    )

    inliers = verify_geometry(
        good_matches,
        keypoints
    )

    print(
        "RANSAC inliers:",
        inliers
    )

    sift_score = calculate_sift_score(
        good_matches,
        inliers
    )

    
    # DINO
    

    print(
        "[4/4] Calculating DINOv2 similarity..."
    )

    dino_similarity = compare_dino(
        image1_path,
        image2_path
    )

    # Convert similarity to percentage
    dino_score = max(
        0,
        min(
            dino_similarity,
            1
        )
    ) * 100

    
    # FINAL SCORE
    

    final_score = (
        0.60 * dino_score +
        0.40 * sift_score
    )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n================================")
    print("MATCHING RESULT")
    print("================================")

    print(
        f"DINOv2 similarity : {dino_score:.2f}%"
    )

    print(
        f"SIFT similarity   : {sift_score:.2f}%"
    )

    print(
        f"Good matches      : {len(good_matches)}"
    )

    print(
        f"RANSAC inliers    : {inliers}"
    )

    print(
        f"FINAL SCORE       : {final_score:.2f}%"
    )

    print("================================")

    return {

        "final_score": round(
            final_score,
            2
        ),

        "dino_score": round(
            dino_score,
            2
        ),

        "sift_score": round(
            sift_score,
            2
        ),

        "good_matches": len(
            good_matches
        ),

        "inliers": inliers
    }


# ============================================================
# 10. RUN TEST
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print("SAMPATTI-SETU IMAGE MATCHER")
    print("================================")

    # Ask user for image paths
    image1_path = input(
        "\nEnter path of first image: "
    ).strip()

    image2_path = input(
        "Enter path of second image: "
    ).strip()

    # Check that files exist
    import os

    if not os.path.isfile(image1_path):
        print(
            f"\nERROR: Image not found: {image1_path}"
        )
        exit()

    if not os.path.isfile(image2_path):
        print(
            f"\nERROR: Image not found: {image2_path}"
        )
        exit()

    # Compare images
    result = compare_images(
        image1_path,
        image2_path
    )

    print("\nFINAL RESULT DICTIONARY:")
    print(result)