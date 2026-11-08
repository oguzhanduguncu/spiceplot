"""spiceplot — ngspice devrelerini arka planda çalıştırıp sonuçlarını numpy / matplotlib ile kullanma.

    from spiceplot import calistir, ciz
    S = calistir('memristor.cir')                 # dosyadan
    S = calistir(metin=netlist_metni)             # metinden (ör. bir döngüde parametre değiştirerek)
    S['i(vi1)'], S['v(a1)'], S['time']            # numpy dizileri; S.adlar() bütün vektörler
    ciz(S, zaman=['v(x1)'], xy=['v(a1):i(vi1)'], atla=1.0, png='sonuc.png')
"""
from .cekirdek import Sonuc, calistir, ciz

__all__ = ['Sonuc', 'calistir', 'ciz']
__version__ = '0.1.0'
