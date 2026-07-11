const fs=require(" fs\);
const p=" D:\\\\__StormShyn\\\\sap-abap-agent\\\\skills\\\\sap-key-user-toolkit\\\\SKILL.md\;
const tk=String.fromCharCode(96);
let s=fs.readFileSync(p," utf8\);
const bad=" license_plate\, " \+tk+\owner\, " \+tk+\registration_date\, " \+tk+\vehicle_type\;
