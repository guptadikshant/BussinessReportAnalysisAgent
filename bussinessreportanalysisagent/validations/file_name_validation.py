import os
from pydantic import BaseModel, field_validator


class AnnualReportFile(BaseModel):
    filename: str
    company_name: str = None
    document_type: str = None
    year: int = None

    @field_validator("filename")
    def validate_filename(cls, v):
        if not v.endswith(".pdf"):
            raise ValueError("File name must end with '.pdf'")
        name_without_ext = v[:-4]
        parts = name_without_ext.split("_")
        if len(parts) < 2:
            raise ValueError("File name must follow the format 'Company_Year.pdf'")
        year_str = parts[-1]
        if not (year_str.isdigit() and len(year_str) == 4):
            raise ValueError("The year must be a four-digit number")
        company_name = "_".join(parts[:-1])
        if company_name == "":
            raise ValueError("Company name cannot be empty")
        return v
    
    def model_post_init(self, __context):
        # Get file extension as document type
        _, ext = os.path.splitext(self.filename)
        self.document_type = ext[1:].lower()  # Remove the dot and convert to lowercase
        
        # Extract company_name and year
        name_without_ext = self.filename[:-(len(self.document_type)+1)]
        parts = name_without_ext.split("_")
        self.company_name = "_".join(parts[:-1])
        self.year = int(parts[-1])


if __name__ == "__main__":
    try:
        file = AnnualReportFile(filename="Company_2024.docx")
        print(file.company_name, file.year, file.document_type)
    except ValueError as e:
        print(e)