function qs(id){return document.getElementById(id)}

const status = qs('status')
const teamcodeInput = qs('teamcode')
const uid1Input = qs('uid1')
const uid2Input = qs('uid2')
const uid3Input = qs('uid3')
const uid4Input = qs('uid4')
const joinBtn = qs('join')
const leaveBtn = qs('leave')
const quickModeToggle = qs('quickmode')
const actionButtons = qs('actionButtons')
const grid = qs('grid')

function setStatus(text, ok=true){
  status.textContent = text
  status.style.borderColor = ok ? '#c6f6d5' : '#fed7d7'
}

// Quick mode applies UI changes and behavior for fast emote
function applyQuickMode(enabled){
  try{
    const uid4Label = qs('uid4').parentElement
    if(enabled){
      if(uid4Label) uid4Label.style.display = 'none'
      if(actionButtons) actionButtons.style.display = 'none'
    } else {
      if(uid4Label) uid4Label.style.display = ''
      if(actionButtons) actionButtons.style.display = ''
    }
  }catch(e){ /* ignore if elements missing */ }
}

if(quickModeToggle){
  quickModeToggle.addEventListener('change', ()=>{
    applyQuickMode(quickModeToggle.checked)
  })
  // initialize
  applyQuickMode(quickModeToggle.checked)
}

// Category filtering
const categoryBtns = document.querySelectorAll('.catbtn')
categoryBtns.forEach(btn => {
  btn.addEventListener('click', ()=>{
    // remove active from all buttons
    categoryBtns.forEach(b => b.classList.remove('active'))
    // add active to clicked button
    btn.classList.add('active')
    
    const category = btn.dataset.category
    const emoteCodes = btn.dataset.emoteCodes
    
    // get all cells
    const cells = grid.querySelectorAll('.cell')
    
    if(category === 'All' || !emoteCodes){
      // show all
      cells.forEach(c => c.style.display = '')
    } else {
      // filter by emote codes
      const codes = emoteCodes.split(',').filter(x=>x.trim())
      cells.forEach(c => {
        const emoteId = c.dataset.emoteId
        // check if emote id starts with any of the codes
        const matches = codes.some(code => emoteId.startsWith(code))
        c.style.display = matches ? '' : 'none'
      })
    }
  })
})

joinBtn.addEventListener('click', async ()=>{
  const teamcode = teamcodeInput.value.trim()
  if(!teamcode){ setStatus('Enter teamcode', false); return }
  setStatus('Joining...')
  try{
    const res = await fetch('/api/join', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({teamcode})})
    const text = await res.text()
    setStatus('Join response: '+text, res.ok)
  }catch(e){ setStatus('Error: '+e.message, false) }
})

leaveBtn.addEventListener('click', async ()=>{
  setStatus('Leaving...')
  try{
    const res = await fetch('/api/leave', {method:'POST'})
    const text = await res.text()
    setStatus('Leave response: '+text, res.ok)
  }catch(e){ setStatus('Error: '+e.message, false) }
})

grid.addEventListener('click', async (ev)=>{
  const img = ev.target.closest('img')
  if(!img) return
  const emoteId = img.dataset.emoteId
  const uid1 = uid1Input.value.trim()
  const uid2 = uid2Input.value.trim()
  const uid3 = uid3Input.value.trim()
  const uid4 = uid4Input.value.trim()
  if(!emoteId){ setStatus('No emote id', false); return }
  setStatus('Sending emote '+emoteId+'...')
  try{
    // If quick mode enabled, call fastemote API with tc and 3 uids
    if(quickModeToggle && quickModeToggle.checked){
      const teamcode = teamcodeInput.value.trim()
      if(!teamcode){ setStatus('Enter teamcode', false); return }
      const payload = {teamcode: teamcode, uid1: uid1, uid2: uid2, uid3: uid3, emote_id: emoteId}
      const res = await fetch('/api/fastemote', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      const text = await res.text()
      setStatus('Fast emote response: '+text, res.ok)
    } else {
      const payload = {emote_id: emoteId}
      if(uid1) payload.uid1 = uid1
      if(uid2) payload.uid2 = uid2
      if(uid3) payload.uid3 = uid3
      if(uid4) payload.uid4 = uid4
      const res = await fetch('/api/emote', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      const text = await res.text()
      setStatus('Emote response: '+text, res.ok)
    }
  }catch(e){ setStatus('Error: '+e.message, false) }
})
