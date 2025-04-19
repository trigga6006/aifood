# backend/services/azure_storage.py

import os
from datetime import datetime, timedelta
import logging
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)

class AzureStorageService:
    def __init__(self):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        self.blob_service_client = None
        self.container_client = None
        
        if self.connection_string and self.container_name:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                self.container_client = self.blob_service_client.get_container_client(self.container_name)
                logger.info(f"Successfully connected to Azure Blob Storage container: {self.container_name}")
            except Exception as e:
                logger.error(f"Failed to connect to Azure Blob Storage: {str(e)}")
        else:
            logger.warning("Azure Blob Storage connection string or container name not provided")
    
    def is_connected(self):
        """Check if the service is properly connected to Azure"""
        return self.blob_service_client is not None and self.container_client is not None
    
    def upload_file(self, file_data, filename=None, content_type=None):
        """
        Upload a file to Azure Blob Storage
        
        Args:
            file_data: The file data to upload
            filename: The name to save the file as (optional)
            content_type: The content type of the file (optional)
            
        Returns:
            dict: Information about the uploaded file
        """
        if not self.is_connected():
            logger.error("Azure Blob Storage is not configured")
            return None
            
        try:
            # Generate a unique filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_file"
            
            # Upload the file
            blob_client = self.container_client.get_blob_client(filename)
            
            content_settings = None
            if content_type:
                from azure.storage.blob import ContentSettings
                content_settings = ContentSettings(content_type=content_type)
                
            blob_client.upload_blob(file_data, overwrite=True, content_settings=content_settings)
            
            # Generate a SAS URL that expires in 1 hour
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=filename,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1)
            )
            
            sas_url = f"{blob_client.url}?{sas_token}"
            
            logger.info(f"File uploaded successfully: {filename}")
            
            return {
                "filename": filename,
                "url": blob_client.url,
                "sas_url": sas_url,
                "size": len(file_data),
                "uploaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to Azure Blob Storage: {str(e)}")
            return None
    
    def get_file(self, filename):
        """
        Get a file from Azure Blob Storage
        
        Args:
            filename: The name of the file to get
            
        Returns:
            bytes: The file data
        """
        if not self.is_connected():
            logger.error("Azure Blob Storage is not configured")
            return None
            
        try:
            blob_client = self.container_client.get_blob_client(filename)
            download_stream = blob_client.download_blob()
            file_data = download_stream.readall()
            
            logger.info(f"File downloaded successfully: {filename}")
            return file_data
            
        except ResourceNotFoundError:
            logger.error(f"File not found in Azure Blob Storage: {filename}")
            return None
        except Exception as e:
            logger.error(f"Error downloading file from Azure Blob Storage: {str(e)}")
            return None
    
    def list_files(self, prefix=None):
        """
        List files in the Azure Blob Storage container
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            list: List of file information
        """
        if not self.is_connected():
            logger.error("Azure Blob Storage is not configured")
            return []
            
        try:
            files = []
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                blob_client = self.container_client.get_blob_client(blob.name)
                
                # Generate a SAS URL that expires in 1 hour
                sas_token = generate_blob_sas(
                    account_name=self.blob_service_client.account_name,
                    container_name=self.container_name,
                    blob_name=blob.name,
                    account_key=self.blob_service_client.credential.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=1)
                )
                
                sas_url = f"{blob_client.url}?{sas_token}"
                
                files.append({
                    "name": blob.name,
                    "url": blob_client.url,
                    "sas_url": sas_url,
                    "size": blob.size,
                    "created_on": blob.creation_time.isoformat() if blob.creation_time else None,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files from Azure Blob Storage: {str(e)}")
            return []
    
    def delete_file(self, filename):
        """
        Delete a file from Azure Blob Storage
        
        Args:
            filename: The name of the file to delete
            
        Returns:
            bool: Whether the deletion was successful
        """
        if not self.is_connected():
            logger.error("Azure Blob Storage is not configured")
            return False
            
        try:
            blob_client = self.container_client.get_blob_client(filename)
            blob_client.delete_blob()
            
            logger.info(f"File deleted successfully: {filename}")
            return True
            
        except ResourceNotFoundError:
            logger.error(f"File not found in Azure Blob Storage: {filename}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file from Azure Blob Storage: {str(e)}")
            return False
