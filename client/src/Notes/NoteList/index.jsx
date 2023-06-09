import React, { useCallback, useEffect, useState } from 'react'
import { PropTypes } from 'prop-types/prop-types'

import { useTheme } from '@emotion/react'
import {
  Checkbox,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography
} from '@mui/material'
import DeleteForeverIcon from '@mui/icons-material/DeleteForever'

import ListHeader from '@/Notes/ListHeader'
import { useDeleteNote, useGetNote, useNotes, useSelectedNote } from '@/store/store-selectors'

const NoteList = React.memo(({ setIsNewNote }) => {
  const [listState, setListState] = useState({
    isAllChecked: false,
    checkedIds: []
  })

  const { palette } = useTheme()
  const notes = useNotes()
  const selectedNote = useSelectedNote()
  const getNote = useGetNote()
  const deleteNote = useDeleteNote()
  
  const handleCheckToggle = useCallback(value => () => {
    const currentIndex = listState.checkedIds.indexOf(value)
    const newCheckedIds = [...listState.checkedIds]

    currentIndex === -1
      ? newCheckedIds.push(value)
      : newCheckedIds.splice(currentIndex, 1)
      
      setListState(prevListState => {
        const isNewAllChecked = !prevListState.isAllChecked && newCheckedIds.length === notes.length
        return ({
      ...prevListState,
      checkedIds: newCheckedIds,
      isAllChecked: isNewAllChecked
    })
  })
  }, [listState.checkedIds, notes.length])

  const handleSelectNote = useCallback(value => () => {
    setIsNewNote(false)
    getNote(value)
  }, [getNote, setIsNewNote])

  const handleDeleteNote = useCallback(id => {
    deleteNote(id)
  }, [deleteNote])

  useEffect(() => {
    if (!notes.length) return setIsNewNote(true)
    if (selectedNote) return setIsNewNote(false)
  }, [notes, notes.length, selectedNote, setIsNewNote])

  return (
    <div
      style={{
        width: 'clamp(225px, 30%, 300px)',
        overflowY: 'auto',
        overflowX: 'hidden',
        paddingTop: 0,
        paddingRight: '0.5rem',
        bgcolor: 'transparent',
        borderRight: `1px solid ${palette.grey[800]}`,
      }}
    >
      <ListHeader listState={listState} setListState={setListState} />
      <List>
        {notes.map(({ id, title, body }) => {
          const labelId = `notes-list-label-${id}`

          return (
            <ListItem
              dense
              disablePadding
              key={labelId}
              sx={{
                borderRadius: '0.5rem',
                paddingLeft: '1rem',
                backgroundColor: id === selectedNote.id ? palette.background.light : 'inherit',
              }}
              secondaryAction={
                <IconButton
                  disableRipple
                  onClick={() => handleDeleteNote(id)}
                  aria-label={`delete-note -${id}`}
                  edge='end'
                  sx={{
                    color: palette.grey[300],
                    '&:hover': { color: palette.primary[200] },
                  }}
                >
                  <DeleteForeverIcon />
                </IconButton>
              }
            >
              <IconButton
                disableRipple
                size='small'
                onClick={handleCheckToggle(id)}
              >
                <ListItemIcon
                  sx={{
                    '&.MuiListItemIcon-root': { minWidth: 'auto' }
                  }}
                >
                  <Checkbox
                    disableRipple
                    edge='start'
                    checked={listState.checkedIds.includes(id)}
                    tabIndex={-1}
                    inputProps={{ 'aria-labelledby': labelId }}
                    sx={{
                      color: palette.grey[300],
                      padding: '9px 3px 9px 9px',
                      '&:hover': { color: palette.primary[200] },
                    }}
                  />
                </ListItemIcon>
              </IconButton>
              <ListItemButton
                role={undefined}
                onClick={handleSelectNote(id)}
                sx={{
                  padding: '0 38px 0 0 !important',
                  '&:hover': { backgroundColor: 'transparent'},
                }}
              >
                <ListItemText
                  id={labelId}
                  sx={{
                    color: palette.secondary[400],
                    '&:hover': { color: palette.primary[200] },
                  }}
                  // take selectedNote as source of truth for title and body, because on update we do not update selectedNote
                  primary={(selectedNote.title && id === selectedNote.id) ? selectedNote.title : title}
                  primaryTypographyProps={{ noWrap: true }}
                  secondary={
                    <Typography
                      noWrap
                      variant='h5'
                      sx={{
                        color: palette.grey[600],
                      }}
                    >
                      {(selectedNote.body && id === selectedNote.id) ? selectedNote.body : body}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </div>
  )
})

NoteList.displayName = '/NoteList'
NoteList.propTypes = {
  setIsNewNote: PropTypes.func,
}

export default NoteList
