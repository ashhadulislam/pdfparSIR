# **Voter Roll PDF Parser using Vision Models**

  

This project attempts to solve the problem of **non-searchable voter roll PDF files** by programmatically extracting information from each voter card using a **Large Vision Model (Gemini 2.5 Flash via OpenRouter)**.

  

The voter roll PDFs contain **30 voter cards per page (10 rows × 3 columns)** starting from **page 3 onward**. Each card contains structured information such as:

-   Serial number
    
-   Name
    
-   Father’s name
    
-   House number
    
-   Age
    
-   Gender
    
-   EPIC ID number
    
-   “Under Adjudication” watermark
    

  

This repository contains tools to:

1.  **Crop voter cards from PDF pages**
    
2.  **Extract structured data from each card using a vision model**
    
3.  **Generate a searchable CSV/Excel file**
    

----------

# **Repository Structure**

```
.
├── app.py
├── vision_model.ipynb
├── requirements.txt
└── README.md
```

----------

# **File Descriptions**

  

## **app.py**

  

app.py is a **Streamlit application** used for **cropping voter cards from the PDF**.

  

### **What it does**

1.  Upload a voter roll PDF.
    
2.  Convert PDF pages into images.
    
3.  Skip the first pages (typically metadata pages).
    
4.  Detect the **10 × 3 grid layout** of voter cards.
    
5.  Crop **30 cards per page**.
    
6.  Save each cropped card as an image file.
    

  

Each card image is saved with:

-   page number
    
-   card index
    

  

Example output:

```
page3_card0.png
page3_card1.png
page3_card2.png
...
```

The app then returns a **ZIP file containing all cropped name cards**.

  

This allows the extraction stage to process each card independently.

----------

## **vision_model.ipynb**

  

This Jupyter notebook performs the **information extraction step** using a **vision model API**.

  

### **Workflow**

1.  Load cropped namecard images from a folder.
    
2.  Convert each image to **base64 format**.
    
3.  Send the image to **Gemini 2.5 Flash via OpenRouter**.
    
4.  Ask the model to extract structured fields.
    
5.  Parse and clean the model response.
    
6.  Save all extracted records to a **CSV file**.
    

----------

# **Extracted Fields**

  

The model extracts the following fields:

-   serial_number
    
-   name
    
-   father_name
    
-   house_number
    
-   age
    
-   gender
    
-   id_number
    
-   under_adjudication
    

  

Additional metadata added by the script:

-   file_identifier
    
-   file_name
    

----------

# **Prompt Used for Extraction**

  

The model is prompted with:

```
Extract the required fields from the image.

Fields:
- serial_number
- name
- father_name
- house_number
- age
- gender
- id_number
- under_adjudication

If watermark "Under Adjudication" is visible (even faint):
    under_adjudication = true
Else:
    under_adjudication = false

Return the extracted values.
No markdown.
No explanation.
```

----------

# **Important Functions in the Notebook**

  

### **namecard_info_extract()**

  

Sends the namecard image to the **OpenRouter API** and retrieves extracted information.

```
namecard_info_extract(api_key, prompt, data_url)
```

Returns a dictionary containing extracted fields.

----------

### **parse_key_value_text()**

  

Parses the model response when returned as:

```
key: value
key: value
```

and converts it into a Python dictionary.

----------

### **clean_answer_list()**

  

Vision models can sometimes return malformed outputs.

  

This function:

-   fixes broken JSON responses
    
-   removes malformed entries
    
-   ensures required fields exist
    

----------

# **Processing Flow**

```
PDF
   ↓
Streamlit App (app.py)
   ↓
Crop 30 cards per page
   ↓
Folder of namecard images
   ↓
vision_model.ipynb
   ↓
Send images to Gemini 2.5 Flash
   ↓
Extract structured information
   ↓
Clean malformed outputs
   ↓
Generate CSV
```

----------

# **Output**

  

The final output is a **searchable CSV file** containing all voter records extracted from the PDF.

  

Example:

```
serial_number,name,father_name,house_number,age,gender,id_number,under_adjudication,file_identifier,file_name
1,Rahim Ali,Karim Ali,23,45,M,ABC1234567,false,roll_136,page3_card0.png
```

----------

# **Setup**

  

Install dependencies:

```
pip install -r requirements.txt
```

Run the cropping app:

```
streamlit run app.py
```

Open the notebook:

```
vision_model.ipynb
```

Add your **OpenRouter API key** before running.

----------

# **Cost Consideration**

  

Processing each namecard requires a **vision model API call**.

  

Approximate cost observed during testing:

-   ~750 cards per PDF
    
-   ~1.5 USD per file
    
-   ~85,000 files total
    

  

Full-scale processing would cost **~$120k**, which is why this repo currently focuses on tooling rather than large-scale deployment.

----------

# **Disclaimer**

  

This project is an **experimental prototype** exploring whether **vision models can make non-searchable public documents searchable**.

  

Accuracy may vary depending on:

-   image quality
    
-   watermark visibility
    
-   OCR clarity
    

----------

# **Future Improvements**

  

Possible improvements:

-   parallel batch processing
    
-   better JSON validation
    
-   retry logic for malformed outputs
    
-   local OCR + LLM hybrid pipeline
    
-   cheaper open-source vision models
    

----------

# **License**

  

Open for experimentation and research use.

