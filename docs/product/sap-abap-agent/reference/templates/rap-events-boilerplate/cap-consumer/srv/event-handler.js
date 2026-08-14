// CAP Event Mesh / messaging consumer stub (rename topic to your RAP event)
// Pair with cds.connect.to('messaging') or S/4 event service binding.
module.exports = async (srv) => {
  const messaging = await cds.connect.to('messaging').catch(() => null)
  if (!messaging) {
    console.warn('messaging destination not bound — event handler idle')
    return
  }
  messaging.on('ObjectCreated', async (msg) => {
    const data = msg.data || {}
    console.log('RAP ObjectCreated', data.salesorderid || data)
    // TODO: persist / call GenAI Hub / notify
  })
}
