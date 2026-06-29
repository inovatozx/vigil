from pydantic import BaseModel, Field
from typing import Optional, List

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The search query to execute.")

class ReadFileSchema(BaseModel):
    path: str = Field(..., description="The path to the file to read.")

class WriteFileSchema(BaseModel):
    path: str = Field(..., description="The path to the file to write.")
    content: str = Field(..., description="The content to write to the file.")
    append: bool = Field(False, description="If true, content will be appended; otherwise, it will overwrite the file.")

class RunShellSchema(BaseModel):
    command: str = Field(..., description="The shell command to execute.")
    timeout: Optional[int] = Field(60, description="Timeout in seconds for the command execution.")

class SendEmailSchema(BaseModel):
    to: List[str] = Field(..., description="List of recipient email addresses.")
    subject: str = Field(..., description="Subject of the email.")
    body: str = Field(..., description="Body content of the email.")
    attachments: Optional[List[str]] = Field(None, description="List of file paths to attach.")

class CreateNoteSchema(BaseModel):
    title: str = Field(..., description="Title of the note.")
    content: str = Field(..., description="Content of the note.")
    tags: Optional[List[str]] = Field(None, description="Optional tags for the note.")

class CreateCalendarEventSchema(BaseModel):
    title: str = Field(..., description="Title of the calendar event.")
    start_time: str = Field(..., description="Start time of the event in ISO 8601 format (e.g., '2024-07-01T10:00:00Z').")
    end_time: str = Field(..., description="End time of the event in ISO 8601 format (e.g., '2024-07-01T11:00:00Z').")
    description: Optional[str] = Field(None, description="Description of the event.")
    attendees: Optional[List[str]] = Field(None, description="List of attendee email addresses.")

class GenerateImageSchema(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation.")
    size: str = Field("1024x1024", description="Desired image size (e.g., '256x256', '512x512', '1024x1024').")
    quality: str = Field("standard", description="Quality of the generated image ('standard' or 'hd').")
    n: int = Field(1, description="Number of images to generate (1-4).")

class SearchMemorySchema(BaseModel):
    query: str = Field(..., description="The query to search through agent's memory.")
    top_k: Optional[int] = Field(5, description="Number of top relevant memories to retrieve.")

class BrowseURLSchema(BaseModel):
    url: str = Field(..., description="The URL to browse.")
    focus: Optional[str] = Field(None, description="Specific topic or question to focus on when browsing the page.")


# Dictionary to map tool names to their schemas
tool_schemas = {
    "web_search": WebSearchSchema,
    "read_file": ReadFileSchema,
    "write_file": WriteFileSchema,
    "run_shell": RunShellSchema,
    "send_email": SendEmailSchema,
    "create_note": CreateNoteSchema,
    "create_calendar_event": CreateCalendarEventSchema,
    "generate_image": GenerateImageSchema,
    "search_memory": SearchMemorySchema,
    "browse_url": BrowseURLSchema,
}

# Function to get JSON schema for a tool
def get_json_schema(tool_name: str) -> Optional[Dict]:
    schema = tool_schemas.get(tool_name)
    if schema:
        return schema.model_json_schema()
    return None
