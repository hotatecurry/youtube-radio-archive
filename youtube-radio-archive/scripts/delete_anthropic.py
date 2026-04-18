import os

DATA_DIR = r"C:\Users\manab\pikuhami\youtube-radio-archive\scripts\data"

anthropic_ids = [
    "-EiQyBZaBLk","EbTGJQR-VyA","Ovnu1X58uxI","PjTKlnaeYUM","AnFlQti0n-c",
    "7ODtHtyui8s","pKqMXXz3yjI","0zg6Mud2X4I","w08lD755Fek","_4axCDBZul4",
    "uy-l9VvjIHU","2xzvHp_cbwQ","9Mm2Ju0H27Y","ZAbrImBRacY","Xb8969kMI3o",
    "LKJkvh_LNuI","XZFCUY7ZTZc","5mqNoeBBDZs","q5i0e_g45bI","1tD_1zgcGhk",
    "Cdp668eDCow","hdr_PMEt23Q","Txeq6vlpjEk","0mHKRBIi3zw","RdD_41X0TKI",
    "rSun9MaPzJo","4regTWX5cro","1QAKnOTIsGI","qvyJ-JmuwyY","EYMtnZljQaQ",
    "TM6FgCTwOkM","KJea6YLn_3k","epnj8wysLEw","FGNBQRQUTOk","ugMRjQXAF6o",
    "uSJInlEGQJw","6BLLstH1J1c","WwwaqKndZyM","HLdEh1LyVHs","N-FPeBqoRZM",
    "8MB-FQ4WE5E","tEURETg4two","Bqd-P7AQwIQ","e1jm1SIUPXI","oznOqJgsnM4",
    "sK91e1_yPGI","pKSUzxGaad4","51AncIvOb40","AHKYNJRWWqs","X9KinROpXKg",
    "G9eZVYLJJDE","vk1e_azF4V0","BZwps9qL9rU","uJEnTTyJRu8","_2WwHRpsnoc",
    "cWLSIbLCSQg","rG2Ftz7mB_Q","NazF5pjJGlg","-I1IWXYHdM0","YlMg_MxKXKE",
    "WP302U8NMAA","s-onmxjFKag","_8qiKoeH5oo","7Sewukv-Bio","4pWBydojp4Q",
    "Tjpzw63K0Ww","4jD1v_-WtLM","De9QW4LlYck","HWvFEPd6ZZw","zXr_DeY0FwI",
    "TlZJtjEKJtI","OwjTxHSeIPw"
]

deleted = 0
for vid_id in anthropic_ids:
    path = os.path.join(DATA_DIR, f"{vid_id}_summary.json")
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️  削除: {vid_id}")
        deleted += 1
    else:
        print(f"⚠️  見つからない: {vid_id}")

print(f"\n✅ {deleted}本削除しました")