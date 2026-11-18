// Flask JSON dates use RFC 1123; parse components to avoid iOS string-date differences.
function timestamp(value) {
  if (typeof value === 'number') return value
  if (typeof value !== 'string') return NaN
  const rfc = value.match(/^(?:\w{3},\s*)?(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})\s+GMT$/)
  if (rfc) {
    const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].indexOf(rfc[2])
    return month < 0 ? NaN : Date.UTC(+rfc[3], month, +rfc[1], +rfc[4], +rfc[5], +rfc[6])
  }
  const iso = value.match(/^(\d{4})[-/](\d{2})[-/](\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?(Z|[+-]\d{2}:?\d{2})?)?$/)
  if (!iso) return NaN
  const parts = [+iso[1], +iso[2] - 1, +iso[3], +(iso[4] || 0), +(iso[5] || 0), +(iso[6] || 0), +(iso[7] || '').padEnd(3, '0').slice(0, 3)]
  if (!iso[8]) return new Date(...parts).getTime()
  const zone = iso[8]
  const offset = zone === 'Z' ? 0 : (zone[0] === '-' ? -1 : 1) * (+zone.slice(1, 3) * 60 + +zone.slice(-2))
  return Date.UTC(...parts) - offset * 60000
}
function formatDate(value) {
  const time = timestamp(value)
  if (!Number.isFinite(time)) return ''
  const date = new Date(time)
  const pad = n => String(n).padStart(2, '0')
  return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())}`
}
module.exports = { timestamp, formatDate }
