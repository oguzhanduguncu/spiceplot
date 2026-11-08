"""spiceplot çekirdeği: ngspice'ı çalıştırma, ASCII raw dosyasını okuma, vektörlere erişim ve çizim."""
import os, re, subprocess, tempfile
import numpy as np


class SpiceHatasi(RuntimeError):
    pass


class Sonuc:
    """Bir ngspice çalıştırmasının sonuçları: S['v(a1)'], S['i(vi1)'], S['time'] → numpy dizisi."""

    def __init__(self, vektorler):
        self._V = vektorler

    def adlar(self):
        return sorted(self._V)

    def __contains__(self, ad):
        try:
            self[ad]; return True
        except KeyError:
            return False

    def __getitem__(self, ad):
        a = ad.strip().lower()
        adaylar = [a]
        m = re.fullmatch(r'i\((.+)\)', a)
        if m:
            adaylar += [f'{m.group(1)}#branch', f'i({m.group(1)}#branch)']
        m = re.fullmatch(r'v\((.+)\)', a)
        if m:
            adaylar += [m.group(1)]
        for k in adaylar:
            if k in self._V:
                return self._V[k]
        raise KeyError(f'"{ad}" bulunamadı. Mevcut vektörler: ' + ', '.join(self.adlar()))

    @property
    def eksen(self):
        """Bağımsız değişken: time (geçici), frequency (AC) ya da tarama değişkeni."""
        for k in ('time', 'frequency', 'v-sweep', 'i-sweep'):
            if k in self._V:
                return self._V[k]
        return next(iter(self._V.values()))


def _raw_oku(yol):
    satir = open(yol, encoding='utf-8', errors='replace').read().splitlines()
    sonuc, i = {}, 0
    while i < len(satir):
        if satir[i].startswith('No. Variables:'):
            nv = int(satir[i].split(':')[1]); npt = int(satir[i + 1].split(':')[1])
            while not satir[i].startswith('Variables:'):
                i += 1
            adlar = [satir[i + 1 + k].split()[1] for k in range(nv)]
            i += nv + 1
            while not satir[i].startswith('Values:'):
                i += 1
            i += 1
            V = np.zeros((npt, nv))
            for p in range(npt):
                for k in range(nv):
                    alan = satir[i].split()[-1]; i += 1
                    V[p, k] = float(alan.split(',')[0]) if ',' in alan else float(alan)   # karmaşık (AC) → gerçel kısım
            sonuc = {ad.lower(): V[:, k] for k, ad in enumerate(adlar)}            # birden fazla analizde SONUNCUSU
            continue
        i += 1
    return sonuc


def calistir(netlist=None, metin=None, klasor=None, zaman_asimi=600):
    """ngspice'ı arka planda çalıştırır (LC_ALL=C — "Türkçe I sorunu"; .control bloğu yok sayılır) → Sonuc.
    netlist: dosya yolu · metin: netlist metni (dosya yerine) · klasor: .include / .lib yollarının göreli olduğu klasör."""
    if (netlist is None) == (metin is None):
        raise ValueError('netlist (dosya yolu) YA DA metin verilmeli')
    if netlist is not None:
        metin = open(netlist, encoding='utf-8', errors='replace').read()
        klasor = klasor or os.path.dirname(os.path.abspath(netlist))
    metin = re.sub(r'(?ims)^\s*\.control\b.*?^\s*\.endc\b[^\n]*\n?', '', metin)
    d = tempfile.mkdtemp(prefix='spiceplot_')
    cir, raw = os.path.join(d, 'devre.cir'), os.path.join(d, 'sonuc.raw')
    open(cir, 'w', encoding='utf-8').write(metin)
    env = dict(os.environ, LC_ALL='C', LANG='C', SPICE_ASCIIRAWFILE='1')
    r = subprocess.run(['ngspice', '-b', '-r', raw, cir], env=env, capture_output=True, text=True,
                       cwd=klasor or os.getcwd(), timeout=zaman_asimi)
    cikti = (r.stdout + r.stderr).splitlines()
    hata = [s for s in cikti if re.search(r'\berror\b', s, re.I)]
    if hata or not os.path.exists(raw):
        raise SpiceHatasi('ngspice hatası:\n  ' + '\n  '.join(hata or cikti[-15:]))
    return Sonuc(_raw_oku(raw))


def ciz(S, zaman=(), xy=(), atla=0.0, png=None, goster=True):
    """zaman: eksene karşı çizilecek vektörler · xy: 'x:y' çiftleri · atla: baştaki bu kadar saniyeyi atla · png: dosyaya kaydet."""
    import matplotlib.pyplot as plt
    t = S.eksen
    m = (t >= atla) if 'time' in S else np.ones(len(t), bool)
    n = (1 if zaman else 0) + len(xy)
    if n == 0:
        raise ValueError('çizilecek bir şey yok: zaman=[…] ya da xy=[…] ver')
    fig, ax = plt.subplots(1, n, figsize=(5.2 * n, 4.2), squeeze=False); ax = ax[0]; k = 0
    if zaman:
        for ad in zaman:
            ax[0].plot(t[m], S[ad][m], lw=1.3, label=ad)
        ax[0].set_xlabel('zaman (s)' if 'time' in S else 'tarama'); ax[0].legend(); ax[0].grid(alpha=0.3); k = 1
    for cift in xy:
        x_, y_ = cift.split(':')
        ax[k].plot(S[x_][m], S[y_][m], lw=1.3)
        ax[k].axhline(0, color='gray', lw=0.6); ax[k].axvline(0, color='gray', lw=0.6)
        ax[k].set_xlabel(x_); ax[k].set_ylabel(y_); ax[k].set_title(f'{y_} – {x_}'); ax[k].grid(alpha=0.3); k += 1
    plt.tight_layout()
    if png:
        plt.savefig(png, dpi=120)
    if goster and not png:
        plt.show()
    return fig
