const OFFSET_MS = Number(process.env.HERA_FAKE_OFFSET_MS || 0);
const RealDate = Date;
const realNow = RealDate.now.bind(RealDate);
class FakeDate extends RealDate {
  constructor(...args) { if (args.length === 0) { super(realNow() - OFFSET_MS); } else { super(...args); } }
  static now() { return realNow() - OFFSET_MS; }
}
globalThis.Date = FakeDate;
