// Set the hardwareConcurrency to 4 (optionally configurable with hardwareConcurrency)
(utils) => {
  utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    'hardwareConcurrency',
    utils.makeHandler().getterValue(opts.hardwareConcurrency)
  )
}, {
  opts: this.opts
}