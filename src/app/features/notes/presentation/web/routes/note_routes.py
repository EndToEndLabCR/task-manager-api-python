from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.features.notes.application.dtos.note_dto import (
    NoteConvertRequest,
    NoteConvertResponse,
    NoteCreateRequest,
    NoteListResponse,
    NoteResponse,
    NoteUpdateRequest,
)
from src.app.features.notes.application.exceptions.note_exception import (
    NoteAccessDeniedException,
    NoteAlreadyConvertedException,
    NoteNotFoundException,
)
from src.app.features.notes.application.use_cases.convert_note import ConvertNoteUseCase
from src.app.features.notes.application.use_cases.create_note import CreateNoteUseCase
from src.app.features.notes.application.use_cases.delete_note import DeleteNoteUseCase
from src.app.features.notes.application.use_cases.get_all_notes import GetAllNotesUseCase
from src.app.features.notes.application.use_cases.get_note_by_id import GetNoteByIdUseCase
from src.app.features.notes.application.use_cases.update_note import UpdateNoteUseCase
from src.app.features.notes.domain.entities.note_type import NoteType
from src.app.features.notes.presentation.web.dependencies import (
    get_convert_note_use_case,
    get_create_note_use_case,
    get_delete_note_use_case,
    get_get_all_notes_use_case,
    get_get_note_by_id_use_case,
    get_update_note_use_case,
)
from src.app.features.auth.presentation.web.dependencies import get_current_user

# Router for endpoints under /api/v1/projects/{project_id}/notes
project_notes_router = APIRouter()

# Router for endpoints under /api/v1/notes/{note_id}
notes_router = APIRouter()


@project_notes_router.post(
    "/{project_id}/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    project_id: UUID,
    payload: NoteCreateRequest,
    current_user=Depends(get_current_user),
    use_case: CreateNoteUseCase = Depends(get_create_note_use_case),
) -> NoteResponse:
    """Create a quick note inside a project workspace."""
    try:
        return await use_case.execute(str(project_id), current_user.id, payload)
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@project_notes_router.get(
    "/{project_id}/notes",
    response_model=NoteListResponse,
)
async def get_all_notes(
    project_id: UUID,
    note_type: Optional[NoteType] = Query(default=None, alias="type"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    current_user=Depends(get_current_user),
    use_case: GetAllNotesUseCase = Depends(get_get_all_notes_use_case),
) -> NoteListResponse:
    """List all notes for a project, with optional type filter and pagination."""
    try:
        return await use_case.execute(str(project_id), current_user.id, note_type, page, size)
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@notes_router.get("/{note_id}", response_model=NoteResponse)
async def get_note_by_id(
    note_id: UUID,
    current_user=Depends(get_current_user),
    use_case: GetNoteByIdUseCase = Depends(get_get_note_by_id_use_case),
) -> NoteResponse:
    """Retrieve a single note by ID."""
    try:
        return await use_case.execute(str(note_id), current_user.id)
    except NoteNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@notes_router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    payload: NoteUpdateRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateNoteUseCase = Depends(get_update_note_use_case),
) -> NoteResponse:
    """Partially update a note's content or type."""
    try:
        return await use_case.execute(str(note_id), current_user.id, payload)
    except NoteNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@notes_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user=Depends(get_current_user),
    use_case: DeleteNoteUseCase = Depends(get_delete_note_use_case),
) -> None:
    """Delete a note permanently."""
    try:
        await use_case.execute(str(note_id), current_user.id)
    except NoteNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@notes_router.post("/{note_id}/convert", response_model=NoteConvertResponse)
async def convert_note(
    note_id: UUID,
    payload: NoteConvertRequest,
    current_user=Depends(get_current_user),
    use_case: ConvertNoteUseCase = Depends(get_convert_note_use_case),
) -> NoteConvertResponse:
    """Convert a RAW note into a TASK or ARCHITECTURE_DECISION."""
    try:
        return await use_case.execute(str(note_id), current_user.id, payload)
    except NoteNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoteAlreadyConvertedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NoteAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
