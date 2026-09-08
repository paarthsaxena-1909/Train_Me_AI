type BrandMarkProps = { light?: boolean }

export function BrandMark({ light = false }: BrandMarkProps) {
  return (
    <div className={`flex items-center gap-2.5 ${light ? 'text-white' : 'text-dark'}`}>
      <span aria-hidden="true" className="grid h-9 w-9 place-items-center rounded-xl bg-orange text-lg font-black text-white">✦</span>
      <span className="text-[17px] font-bold tracking-[-0.04em]">Train Me<span className={light ? 'text-light-purple' : 'text-primary'}>.</span></span>
    </div>
  )
}
