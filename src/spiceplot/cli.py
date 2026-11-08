"""Komut satırı: spiceplot devre.cir --zaman "v(x1)" --xy "v(a1):i(vi1)" [--atla 1] [--png sonuc.png] [--liste]"""
import argparse, sys
from .cekirdek import SpiceHatasi, calistir, ciz


def main():
    ap = argparse.ArgumentParser(prog='spiceplot', description='ngspice devresini arka planda çalıştırıp çizer')
    ap.add_argument('netlist'); ap.add_argument('--zaman', nargs='*', default=[]); ap.add_argument('--xy', nargs='*', default=[])
    ap.add_argument('--atla', type=float, default=0.0, help='baştaki bu kadar saniyeyi atla (geçiş dönemi)')
    ap.add_argument('--png', help='grafiği bu dosyaya kaydet'); ap.add_argument('--liste', action='store_true', help='vektör adlarını listele')
    a = ap.parse_args()
    try:
        S = calistir(a.netlist)
        if a.liste or not (a.zaman or a.xy):
            print('vektörler:', ', '.join(S.adlar())); return
        ciz(S, zaman=a.zaman, xy=a.xy, atla=a.atla, png=a.png)
        if a.png:
            print('kaydedildi:', a.png)
    except (SpiceHatasi, KeyError) as e:
        sys.exit(str(e).strip('"'))


if __name__ == '__main__':
    main()
