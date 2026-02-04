# Mobile Long-Press Testing Guide

## Quick Start

### Test on Mobile Device or Chrome DevTools Mobile Emulation

#### Step 1: Open Chat Application
```bash
# Start the Flask app
python app.py
```
Navigate to: `http://localhost:5000/student-dashboard`
Click on "Chat" → Opens chat interface

#### Step 2: Test Desktop Right-Click (Control Test)
1. Right-click on a conversation → Menu appears at cursor
2. Right-click on a message → Menu appears at cursor
3. Click elsewhere → Menus close

This confirms desktop functionality works as baseline.

---

## Mobile Testing Procedure

### Option A: Physical Mobile Device
1. Connect to same WiFi as development machine
2. Open browser on phone → `http://<your-ip>:5000/student-dashboard`
3. Navigate to Chat
4. Follow test cases below

### Option B: Chrome DevTools Mobile Emulation
1. Open Chrome DevTools (F12)
2. Click "Toggle device toolbar" (⌘+Shift+M on Mac, Ctrl+Shift+M on Windows)
3. Select device (e.g., "iPhone 13")
4. Follow test cases below

---

## Test Cases

### TC-001: Conversation Long-Press Detection

**Setup**: Open chat with list of conversations visible

**Steps**:
1. Long-press on a conversation item for 500ms (hold finger down)
2. Observe context menu appears at touch point
3. Release finger
4. Verify menu stays visible

**Expected Results**:
- ✅ Menu appears at exact touch location
- ✅ Menu has 11 buttons (View Info, Mark Read/Unread, Mute/Unmute, Pin/Unpin, Archive/Unarchive, Block, Delete)
- ✅ Menu has proper styling and shadow

**Actual Result**: _______________

---

### TC-002: Conversation Quick Tap

**Setup**: Chat with multiple conversations

**Steps**:
1. Quickly tap (< 200ms) a conversation
2. Observe result

**Expected Results**:
- ✅ Conversation opens (no menu shows)
- ✅ No lag or delay in opening

**Actual Result**: _______________

---

### TC-003: Conversation Scroll vs Long-Press

**Setup**: Chat with scrollable conversation list

**Steps**:
1. Press and hold on conversation
2. While holding, move finger 15px down (scroll motion)
3. Release

**Expected Results**:
- ✅ List scrolls normally
- ✅ Menu does NOT appear
- ✅ No false positives on intentional scrolling

**Actual Result**: _______________

---

### TC-004: Message Long-Press Detection

**Setup**: Open a conversation with multiple messages

**Steps**:
1. Long-press on a message bubble for 500ms
2. Observe context menu appears
3. Release finger

**Expected Results**:
- ✅ Menu appears at touch point
- ✅ Menu has 6 buttons (Reply, Edit*, Copy, Forward, Delete*, React)
- ✅ Edit/Delete hidden if message from another user

**Actual Result**: _______________

---

### TC-005: Message Menu Actions - Reply

**Setup**: Message menu visible after long-press

**Steps**:
1. Tap "Reply" button
2. Observe input field and reply UI
3. Type a reply message
4. Send

**Expected Results**:
- ✅ Menu closes
- ✅ Input field shows reply preview
- ✅ Message sends as reply
- ✅ Reply quote appears in sent message

**Actual Result**: _______________

---

### TC-006: Message Menu Actions - Copy

**Setup**: Message menu visible, message selected

**Steps**:
1. Tap "Copy" button
2. Open any text field
3. Long-press to paste

**Expected Results**:
- ✅ Success toast appears
- ✅ Text is copied to clipboard
- ✅ Paste works elsewhere

**Actual Result**: _______________

---

### TC-007: Message Menu Actions - React

**Setup**: Message menu visible

**Steps**:
1. Tap "React" button
2. Observe emoji picker
3. Select an emoji

**Expected Results**:
- ✅ Emoji picker appears
- ✅ Emoji picker has 8+ preset emojis
- ✅ Emoji adds to message
- ✅ Emoji reaction shows on message

**Actual Result**: _______________

---

### TC-008: Message Menu Actions - Forward

**Setup**: Message menu visible

**Steps**:
1. Tap "Forward" button
2. Observe forward dialog
3. Select target conversation
4. Tap "Forward" button in dialog

**Expected Results**:
- ✅ Dialog opens with conversation list
- ✅ Current conversation filtered out
- ✅ Can select any other conversation
- ✅ Message forwards with "[Forwarded]" prefix

**Actual Result**: _______________

---

### TC-009: Menu Close on Tap Outside

**Setup**: Either conversation or message menu visible

**Steps**:
1. Tap somewhere else on screen (not on menu)

**Expected Results**:
- ✅ Menu disappears
- ✅ No action triggered from tap location

**Actual Result**: _______________

---

### TC-010: Menu Close on Screen Orientation

**Setup**: Menu visible on portrait orientation

**Steps**:
1. Rotate device to landscape
2. Observe

**Expected Results**:
- ✅ Menu closes gracefully
- ✅ No JavaScript errors in console
- ✅ Layout adjusts properly

**Actual Result**: _______________

---

### TC-011: Touch Precision

**Setup**: Crowded message list with multiple messages

**Steps**:
1. Tap different messages in sequence
2. Long-press on each one
3. Verify correct menu appears

**Expected Results**:
- ✅ Correct message menu appears
- ✅ No menu mixup between messages
- ✅ Touch targeting is accurate

**Actual Result**: _______________

---

### TC-012: Edit Action - Own Message

**Setup**: Long-press on own message

**Steps**:
1. Tap "Edit" button
2. Observe edit prompt
3. Modify text
4. Confirm

**Expected Results**:
- ✅ Edit button is visible
- ✅ Prompt shows current message text
- ✅ Edit is accepted and updates message
- ✅ "(edited)" tag shows on message

**Actual Result**: _______________

---

### TC-013: Edit Action - Other's Message

**Setup**: Long-press on message from another user

**Steps**:
1. Observe context menu

**Expected Results**:
- ✅ Edit button is HIDDEN
- ✅ Delete button is HIDDEN
- ✅ Other buttons are visible

**Actual Result**: _______________

---

### TC-014: Delete Confirmation

**Setup**: Long-press on own message

**Steps**:
1. Tap "Delete" button
2. Confirm in dialog

**Expected Results**:
- ✅ Confirmation dialog appears
- ✅ Message removed after confirmation
- ✅ Can cancel without deleting

**Actual Result**: _______________

---

### TC-015: Conversation Actions

**Setup**: Long-press conversation, menu visible

**Steps**:
1. Test each conversation menu action:
   - Mark Unread → Badge appears
   - Mark Read → Badge disappears
   - Mute → Muted icon shows
   - Unmute → Muted icon disappears
   - Pin → Moves to top
   - Unpin → Returns to position
   - Archive → Conversation grayed out
   - Unarchive → Normal appearance
   - Block → Confirmation dialog

**Expected Results**:
- ✅ All 11 actions work correctly
- ✅ UI updates immediately
- ✅ No console errors
- ✅ No network failures

**Actual Result**: _______________

---

## Browser Console Checks

### While Testing:
1. Open DevTools Console (F12 → Console tab)
2. Perform long-press actions
3. Check for errors

**Expected**:
```javascript
// You should see logs like:
📤 Forward dialog opening...
🔔 Forward button clicked
📋 3 conversations available
📤 Sending: {...}
Response: 200
✅ Forward handler attached
```

**Check**:
- ✅ No red error messages
- ✅ No `undefined` errors
- ✅ Touch events firing (if console.log added)

---

## Performance Checks

### Touch Response Time
- **Expected**: Menu appears < 100ms after releasing touch
- **Actual**: ________________

### Scroll Performance
- **Expected**: Smooth scrolling, no jank
- **Actual**: ________________

### Memory
- **Expected**: No memory leaks after 100+ long-press actions
- **Actual**: ________________

---

## Accessibility Testing

### Screen Reader (if available)
1. Enable screen reader (VoiceOver/TalkBack)
2. Long-press menu
3. Verify menu items are readable

### Keyboard Navigation
1. On desktop, test Tab key navigation
2. Verify arrow keys work in emoji picker
3. Verify Escape closes menus

---

## Sign-Off

| Tester Name | Date | Device | Result |
|-----------|------|--------|--------|
|           |      |        | ✅ PASS / ❌ FAIL |
|           |      |        | ✅ PASS / ❌ FAIL |
|           |      |        | ✅ PASS / ❌ FAIL |

---

## Known Issues & Workarounds

### Issue: Menu appears off-screen on small devices
**Workaround**: CSS will auto-adjust menu position

### Issue: Touch feels sluggish on slow devices
**Workaround**: 500ms delay is intentional to prevent accidental presses

### Issue: Double-tap zoom triggers menu
**Workaround**: Not a problem since long-press requires hold time

---

## Regression Testing

Before shipping, test these unchanged features still work:

- ✅ Desktop right-click menus
- ✅ Message search
- ✅ Group member settings
- ✅ New conversation creation
- ✅ Typing indicators
- ✅ Read receipts
- ✅ Online status
- ✅ Message notifications
