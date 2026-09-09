module.exports = async (srv) => {
  const { Items } = srv.entities
  srv.before('CREATE', Items, (req) => {
    if (!req.data.title) req.error(400, 'title is required')
  })
}
