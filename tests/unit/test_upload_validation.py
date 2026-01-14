import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import UploadFile, HTTPException
from dxf_generator.interface.routes.parser import parse_dxf
from dxf_generator.config.env_config import config

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def mock_upload_file():
    file = MagicMock(spec=UploadFile)
    file.filename = "test.dxf"
    file.content_type = "application/dxf" # Default valid type
    file.read = AsyncMock()
    return file

@pytest.mark.anyio
async def test_upload_valid_extension(mock_upload_file):
    mock_upload_file.filename = "test.dxf"
    mock_upload_file.content_type = "application/dxf"
    mock_upload_file.read.side_effect = [b"content", b""] # Simulate read
    
    with patch("dxf_generator.interface.routes.parser.open", MagicMock()), \
         patch("dxf_generator.interface.routes.parser.DXFService.parse") as mock_parse:
        
        mock_parse.return_value = {"type": "ibeam", "data": {}}
        await parse_dxf(mock_upload_file)
        # Should succeed without error

@pytest.mark.anyio
async def test_upload_invalid_extension(mock_upload_file):
    mock_upload_file.filename = "test.exe"
    mock_upload_file.content_type = "application/x-msdos-program"
    
    with pytest.raises(HTTPException) as exc:
        await parse_dxf(mock_upload_file)
    
    assert exc.value.status_code == 400
    assert "Invalid file type" in exc.value.detail

@pytest.mark.anyio
async def test_upload_invalid_content_type(mock_upload_file):
    mock_upload_file.filename = "test.dxf"
    mock_upload_file.content_type = "application/pdf" # Invalid type
    
    with pytest.raises(HTTPException) as exc:
        await parse_dxf(mock_upload_file)
    
    assert exc.value.status_code == 400
    assert "Invalid content type" in exc.value.detail

@pytest.mark.anyio
async def test_upload_size_limit_exceeded(mock_upload_file):
    mock_upload_file.filename = "large.dxf"
    mock_upload_file.content_type = "application/dxf"
    
    # Simulate large content > 5MB
    large_chunk = b"x" * (config.UPLOAD_MAX_SIZE_BYTES + 100)
    mock_upload_file.read.side_effect = [large_chunk, b""]
    
    with patch("dxf_generator.interface.routes.parser.open", MagicMock()), \
         patch("dxf_generator.interface.routes.parser.remove_file") as mock_remove:
        
        with pytest.raises(HTTPException) as exc:
            await parse_dxf(mock_upload_file)
            
        assert exc.value.status_code == 400
        assert "exceeds limit" in exc.value.detail
        mock_remove.assert_called()
