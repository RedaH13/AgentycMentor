export interface UploadResponse {
    session_id: string;
    data: {
        extracted_text: string;
    };
    langue: string;
}
