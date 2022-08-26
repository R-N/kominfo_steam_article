import streamlit as st
import pandas as pd
from ..functions.twitter import POLARITY_LABEL_VOLUME_COLS as TWITTER_POLARITY_LABEL_VOLUME_COLS, QUERIES as TWITTER_QUERIES, EXCLUDE_QUERIES as TWITTER_EXCLUDE_QUERIES, POLARITY_LABEL_COLS as TWITTER_POLARITY_LABEL_COLS, LABELS as TWITTER_LABELS, INCLUDE_QUERIES as TWITTER_INCLUDE_QUERIES, DATES as TWITTER_DATES
from ..functions.twitter import load_all as twitter_load_all, aggregate_data as twitter_aggregate_data, filter_query as twitter_filter_query, merge_data as twitter_merge_data
from ..display.twitter import tweet_volume_bar_stack, tweet_slides, display_tweet
from ..display.steam import game_bar_horizontal, game_scatter, show_metrics as steam_show_metrics, game_histogram, limit_df as steam_limit_df, game_availabiltiy_pie, show_metrics_table as steam_show_metrics_table, groupby_tag_2 as steam_groupby_tag_2
from ..global_data import Constants
from ..functions.steam import LABELS as STEAM_LABELS
from ..functions.gtrends import LABELS as GTRENDS_LABELS, DEFAULT_COLS_1 as GTRENDS_DEFAULT_COLS_1
from ..functions.gtrends import load_df as gtrends_load_df
from ..display.gtrends import trend_line
from ..display.util import selectbox_2, multiselect_2
from ..functions.steam import split_by_availability as steam_split_by_availabiltiy, init_df as steam_init_df
from ..pages.twitter import tweet_section, sentiment_section as tweet_sentiment_section, volume_section as tweet_volume_section
from ..pages.gtrends import gtrends_section
from ..pages.steam import histogram_section as steam_histogram_section, scatter_section as steam_scatter_section, bar_horizontal_section as steam_bar_horizontal_section
import json


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def load_data_twitter():
    all_data = twitter_load_all()
    aggregate = twitter_aggregate_data(all_data)

    return all_data, aggregate
    
st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def load_data_steam():
    with open(Constants.steam_appid_path) as f:
        steam_appids = json.load(f)
    df = pd.read_excel(Constants.steam_path, sheet_name="data")
    df["count"] = 1
    steam_init_df(df)

    return df

def app():
    all_data, aggregate = load_data_twitter()
    df = load_data_steam()
    df_paid, df_free, df_unavailable, df_unreleased = steam_split_by_availabiltiy(df)

    st.title("Steam, Pintu Ekspor Terbesar Industri Game PC Indonesia yang Ditutup oleh Kominfo")
    st.write('<span class="h3">Muhammad Rizqi Nur, 2022</span>', unsafe_allow_html=True)
    st.markdown("### [Artikel versi sebelumnya (TextBlob)](https://r-n-kominfo-steam-article-app-v1-1-y6k8hj.streamlitapp.com/)", unsafe_allow_html=True)

    col1, col2 = st.columns((1, 1))
    col1.image("assets/img/blokirkominfo.png")
    col2.image("assets/img/letmein steam.png")
    col2.caption("Insiden pemblokiran Steam oleh Kominfo, circa 2022, memeized")

    col1.markdown('''
    <p class="text-justify">
        <span class="">H</span>ari <strong>Sabtu 30 Juli 2022</strong> lalu, terkait aturan PSE, <strong>Kominfo telah memblokir</strong> beberapa layanan besar dari luar negeri, salah satunya <strong>Steam</strong>. 
        Pemblokiran ini menghebohkan media internet Indonesia dan langsung menjadi <strong>trending twitter</strong>. 
        <strong>Mayoritas</strong> sentimen <strong>tweet negatif</strong>, sedangkan yang positif sangat sedikit. 
        Bagaimana tidak, setelah melalui 5 hari kerja yang panjang, orang-orang Indonesia ternyata tidak dapat refreshing dengan game yang telah dibeli; semua karena suatu regulasi baru dari pemerintah. 
        Bukan cuma tempat membeli game, Steam juga adalah <strong>pintu ekspor terbesar industri game PC Indonesia</strong>. 
        Developer Indonesia diestimasikan telah meraup sebanyak <strong>1,66 miliar</strong> rupiah, dimana <strong>1,58 miliar</strong> rupiah di antaranya berasal <strong>dari game indie</strong>. 
        Developer game indie <strong>tidak memiliki sponsor</strong> besar dalam pembuatannya, dan industri game di Indonesia sendiri terbilang kecil, tapi <strong>Steam memungkinkan mereka menjual ke seluruh dunia</strong>.
        Sepenting itu lah Steam bagi industri dan pasar game Indonesia. Untungnya, per tanggal <strong>2 Agustus 2022</strong>, akses <strong>Steam telah dibuka</strong> kembali.
    </p>
    ''', unsafe_allow_html=True)

    st.markdown("## Sudah dari seminggu, dua minggu, setahun, dan dua tahun sebelumnya")
    st.container().markdown('''
    <p class="text-justify">
        Pemblokiran yang menyebabkan kehebohan ini dilakukan karena <strong>aturan PSE</strong>, dimana setiap penyelenggara sistem elektronik wajib mendaftar dan memenuhi aturan yang berlaku. 
        Aturan ini sudah ada sejak tahun  <strong>2020</strong> dan pendaftarannya sudah dibuka sejak  <strong>2 Juni 2021</strong>.
        Wacana pemblokiran PSE ini sendiri sudah ada dari <strong>dua minggu sebelumnya</strong> dengan <strong>Google, Whatsapp, dan Instagram</strong> sebagai topik dan deadline <strong>20 Juli 2022</strong>, tapi pada akhirnya mereka  <strong>telah mendaftar</strong> dan topik pemblokiran PSE mulai surut. 
        Dua, tiga hari berlalu, masih tidak terjadi apa-apa; ancaman pemblokiran seperti ancaman kosong. 
        Ternyata Kominfo tidak langsung melakukan pemblokiran, tapi memberi <strong>surat teguran</strong> pada tanggal <strong>23 Juli 2022</strong> dan <strong>memperpanjang batas pendaftaran</strong> hingga satu minggu setelahnya, yaitu <strong>29 Juli 2022</strong>. 
        Karena tidak kunjung mendaftar, beberapa layanan besar akhirnya diblokir, salah satunya Steam. 
    </p>
    ''', unsafe_allow_html=True)

    st.markdown("# Trending")

    col2, col1 = st.columns((1, 1))
    col1.markdown("## 41 ribu tweet dalam sehari")
    col1.markdown('''
    <p class="text-justify">
        Pada tanggal pemblokiran, yaitu <strong>30 Juli 2022</strong>, tweet mengenai kominfo memuncak hingga <strong>41.645</strong> tweet publik. Jumlah ini <strong>tanpa menghitung retweet dan quote</strong>.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Mayoritas sentimen negatif, sangat sedikit yang positif")
    col1.markdown('''
    <p class="text-justify">
        Analisis sentimen dilakukan menggunakan <strong>IndoBERT</strong> untuk tweet berbahasa Indonesia dan <strong>BERTsent</strong> untuk tweet berbahasa Inggris. Tiap <strong>tweet diboboti</strong> sebanyak max(like, retweet)+1.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Pencarian DNS meningkat drastis, tapi VPN tidak")
    col1.markdown('''
    <p class="text-justify">
        Masyarakat pasti mencari solusi untuk mengatasi pemblokiran. Anehnya, pencarian keyword DNS meningkat drastis, tapi pencarian keyword "<strong>vpn</strong>" <strong>hanya meningkat sedikit</strong>. Ini berarti <strong>DNS adalah solusi favorit</strong> masyarakat untuk pemblokiran, <strong>bukan VPN</strong>.
    </p>
    ''', unsafe_allow_html=True)

    tab_volume, tab_sentiment, tab_gtrends = col2.tabs(["Volume", "Sentimen", "Google Trends"])
    tweet_volume_section(tab_volume, aggregate, compact=True, key="volume_home")
    tweet_sentiment_section(tab_sentiment, aggregate, compact=True, key="sentiment_home")
    gtrends_section(tab_gtrends, key="trends_home")

    tweet_section(st, all_data, compact=True, key="tweet_home")

    st.markdown("# Steam dan GameDev Indonesia")

    col1, col2 = st.columns((1, 1))
    #col2.image("assets/img/logo_steam.svg")
    col2.write('''
    <img 
        src="https://store.cloudflare.steamstatic.com/public/shared/images/header/logo_steam.svg"
        class="center"
    >
    '''.replace("\n", " "), unsafe_allow_html=True)

    col1.markdown("## Platform digital distribusi game PC terbesar di dunia")
    col1.markdown('''
    <p class="text-justify">
        Pada tahun 2013, Steam memiliki <strong>75% pangsa pasar</strong>. Pada tahun 2017, Steam telah menjual sebanyak <strong>4.3 miliar USD</strong>. Pada tahun 2021, Steam sudah memiliki lebih dari <strong>34.000 game</strong> dengan lebih dari <strong>132 juta pengguna aktif per bulan</strong>.
    </p>
    ''', unsafe_allow_html=True)

    #col1, col2 = st.columns((1, 1))

    col2.image("assets/img/steam sea.jpg")
    col2.caption("Virtual SEASia, 2020")
    col1.markdown("## Game Indonesia paling banyak di Asia Tenggara")
    col1.markdown('''
    <p class="text-justify">
        Menurut VirtualSEA pada tahun 2020, <strong>Indonesia paling banyak</strong> mendaftarkan game di Steam di antara negara-negara Asia Tenggara lainnya. Pada tahun tersebut, terdaftar <strong>124 game dari developer Indonesia</strong>. Angka ini meliputi game yang pada saat itu belum rilis atau early-access.
    </p>
    ''', unsafe_allow_html=True)


    col2, col1 = st.columns((1, 1))
    
    tab_histogram, tab_scatter, tab_pie = col2.tabs(["Histogram", "Scatter Plot", "Ketersediaan Game"])
    steam_histogram_section(tab_histogram, df_paid, compact=True, key="revenue_home")
    steam_scatter_section(tab_scatter, df_paid, compact=True, key="revenue_home", index="name")
    
    game_availabiltiy_pie(
        tab_pie,
        len(df_paid),
        len(df_free),
        len(df_unavailable),
        len(df_unreleased)
    )

    col1.markdown("## Pintu ekspor terbesar industri game PC Indonesia")
    col1.markdown('''
    <p class="text-justify">
        Developer Indonesia diestimasikan telah meraup sebanyak <strong>1,66 miliar rupiah</strong>. Angka ini didapat dengan mengalikan <strong>harga saat ini</strong> (tanpa diskon) dengan <strong>jumlah review positif</strong>. Mulai titik ini, <strong>hanya 132 game berbayar</strong> yang diperhitungkan.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Mayoritas Game Indie")
    col1.markdown('''
    <p class="text-justify">
        Sebesar <strong>1,58 miliar rupiah</strong> dari 1,66 miliar rupiah tadi didapat oleh game indie. Developer game indie <strong>tidak memiliki sponsor</strong> besar dalam pembuatannya, dan industri game di Indonesia sendiri terbilang kecil, tapi <strong>Steam memungkinkan mereka menjual ke seluruh dunia</strong>.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Penjualan tertinggi 437,3 juta rupiah")
    col1.markdown('''
    <p class="text-justify">
        Estimasi penjualan terbesar <strong>437,3 juta rupiah</strong> oleh <strong>Toge Productions</strong> dengan <strong>Coffee Talk</strong>, yang juga merupakan sebuah <strong>game indie</strong>.
    </p>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns((4, 5))
    tab_genre, tab_category, tab_platform = col2.tabs(["Genre", "Category", "Platform"])
    steam_bar_horizontal_section(
        tab_genre, 
        df_paid, 
        y="genres", 
        compact=True,
        key="genres_home"
    )
    steam_bar_horizontal_section(
        tab_category, 
        df_paid, 
        y="categories", 
        compact=True,
        key="categories_home"
    )
    steam_bar_horizontal_section(
        tab_platform, 
        df_paid, 
        y="platforms", 
        compact=True,
        key="platforms_home"
    )
    col1.markdown("## Adventure adalah genre terfavorit")
    col1.markdown('''
    <p class="text-justify">
        Game Indonesia di Steam didominasi oleh <strong>genre adventure, casual, dan action</strong>, tapi kalau <strong>dilihat dari popularitas, genre adventure jauh meninggalkan yang lain</strong>.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Hampir semuanya single-player")
    col1.markdown('''
    <p class="text-justify">
        Sebagian besar game Indonesia merupakan game <strong>single-player</strong> dengan fitur <strong>steam achievement, steam cloud, dan steam trading cards</strong>. 
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Windows.")
    col1.markdown('''
    <p class="text-justify">
        <strong>Semua</strong> game Indonesia mendukung sistem operasi <strong>Windows</strong>. Hampir setengahnya juga mendukung <strong>MacOS</strong>, tapi hanya sedikit yang mendukung <strong>Linux</strong>. 
    </p>
    ''', unsafe_allow_html=True)
    col2, col1 = st.columns((2, 1))
    tab_lang, tab_voice = col2.tabs(["Bahasa", "Voice"])
    steam_bar_horizontal_section(
        tab_lang, 
        df_paid, 
        y="supported_languages", 
        compact=True,
        key="lang_home"
    )
    steam_bar_horizontal_section(
        tab_voice, 
        df_paid, 
        y="supported_languages_voice", 
        compact=True,
        key="voice_home"
    )
    col1.markdown("## Bahasa Inggris. Bahasa Indonesia?")
    col1.markdown('''
    <p class="text-justify">
        <strong>Semua</strong> game Indonesia mendukung bahasa <strong>Inggris</strong>, tapi game-game populer juga mendukung bahasa lain seperti bahasa <strong>Cina, Jepang, Spanyol, Rusia, Jerman, Portugis-Brazil, Prancis hingga Korea</strong>. Sayangnya, di Steam <strong>tidak ada tag Bahasa Indonesia</strong>, jadi kita tidak bisa mencari game berbahasa Indonesia melalui tag.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Sebagian besar tanpa <i>voice</i>", unsafe_allow_html=True)
    col1.markdown('''
    <p class="text-justify">
        Sebagian besar game Indonesia tidak mendukung voice, tapi dari yang mendukung voice, <strong>Bahasa Inggris paling banyak</strong>.
    </p>
    ''', unsafe_allow_html=True)

    """
    labels = {
        None: "Tanpa pengelompokan",
        "developers": "Developer",
        "publishers": "Publisher"
    }
    df_grouped, grouping = steam_groupby_tag_2(df_paid, labels)
    if grouping:
        tab_histogram, tab_scatter = st.tabs(["Histogram", "Scatter plot"])
    else:
        tab_bar, tab_histogram, tab_scatter = st.tabs(["Bar chart horizontal", "Histogram", "Scatter plot"])
        steam_bar_horizontal_section(tab_bar, df_grouped)
    steam_histogram_section(tab_histogram, df_grouped)
    steam_scatter_section(tab_scatter, df_grouped)
    """
    
    col1, col2 = st.columns((2, 3))
    tab_histogram, tab_scatter = col2.tabs(["Histogram", "Scatter"])
    steam_histogram_section(
        tab_histogram, 
        df_paid, 
        limit=10 * 10**6,
        compact=True, 
        key="bad_home"
    )
    steam_scatter_section(
        tab_scatter,
        df_paid,
        y_options=["estimated_revenue", "estimated_revenue_positive"],
        hlines={
            "10 juta": 10 * 10**6, 
            "Median": df_paid.median(), 
            "Mean": df_paid.mean()
        },
        compact=True,
        key="bad_home",
        index="name"
    )
    col1.markdown("## Sekarang, kabar buruknya", unsafe_allow_html=True)
    col1.markdown('''
    <p class="text-justify">
        <strong>Dari 132 game</strong> Indonesia yang telah rilis dan masih ada di Steam, sekitar <strong>setengahnya</strong> diestimasikan hanya menjual sekitar <strong>satu juta rupiah ke bawah (median 1.16 juta)</strong>.
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("## Hanya 23 game yang sukses", unsafe_allow_html=True)
    col1.markdown('''
    <p class="text-justify">
        <strong>Sebanyak 109 dari 132 game</strong> diestimasikan hanya berhasil <strong>menjual di bawah 10 juta rupiah</strong>. Padahal, waktu, tenaga, dan uang yang diperlukan untuk mengembangkan game cukup besar, sedangkan <strong>developer indie sulit mencari dana</strong>. Industri yang sudah sulit ini akan jadi jauh lebih sulit lagi jika Steam benar-benar diblokir.
    </p>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns((1, 1))
    col1.markdown("# Unblock")
    col2.image("assets/img/Lah green tunnel.png")
    #col2.caption("hehe")
    col1.markdown('''
    <p class="text-justify">
        Untungnya, <strong>akses ke Steam telah dibuka kembali</strong> per tanggal <strong>2 Agustus 2022</strong>. Namun, jika lagi-lagi aturan PSE memblokir suatu layanan penting, Anda bisa gunakan salah satu aplikasi ini:
    </p>
    ''', unsafe_allow_html=True)
    col1.markdown("- [Simple DNSCrypt (Windows)](https://simplednscrypt.org/)")
    col1.markdown("- [Green Tunnel (Windows, Linux, MacOS)](https://github.com/SadeghHayeri/GreenTunnel)")
    col1.markdown("- [DPITunnel v2 (Linux & Android, perlu root)](https://github.com/zhenyolka/DPITunnel-android)")
    col1.markdown("- [PowerTunnel (Windows & Android)](https://github.com/krlvm/PowerTunnel)")
    col1.markdown('''
    <p class="text-justify">
        Meskipun ada cara bypass pemblokiran, ini <strong>hanya solusi sementara</strong>. Jika benar-benar diblokir permanen, suatu layanan akan menjadi <strong>ilegal</strong>. Ini berarti meskipun kita bisa bypass blokir, pemberi layanan <strong>tidak dapat mendukung Indonesia</strong>. Contohnya, kalian akan <strong>kesulitan topup</strong> dengan rupiah.
    </p>
    ''', unsafe_allow_html=True)

    st.markdown("# Eksplorasi")
    st.markdown("Ada yang ingin kalian ketahui lebih lanjut? Merasa ada yang saya lewatkan? Ingin lihat grafik dengan ukuran lebih besar? Coba klik tombol di pojok kiri atas.")

    st.markdown("# Tutorial")
    st.markdown("Ingin belajar membuat sesuatu seperti ini? Saya menulis beberapa artikel panduan di Medium.")
    col1, col2 = st.columns(2)
    col1.markdown("- [Analisis Sentimen Twitter Berbahasa Indonesia Menggunakan Pretrained Neural Network Transformer (BERT)](https://medium.com/@rizqinur2010/analisis-sentimen-twitter-berbahasa-indonesia-menggunakan-pretrained-neural-network-transformer-d4de29f64ebe)")
    col2.markdown("- [Scraping Ringkasan Review Keseluruhan dan Detail Game Steam dari Steam Curator List](https://medium.com/@rizqinur2010/scraping-ringkasan-review-keseluruhan-dan-detail-game-steam-dari-steam-curator-list-a7b5b3834e48)")

    st.markdown("# Referensi")
    col2, col1 = st.columns(2)
    col1.markdown("- [IndoBERT Sentiment](https://huggingface.co/mdhugol/indonesia-bert-sentiment-classification)")
    col1.markdown("- [BERTsent Sentiment](https://huggingface.co/rabindralamsal/BERTsent)")
    col1.markdown("- [Games from Indonesia (Part 2)](https://store.steampowered.com/curator/25278687-Virtual-SEA-Games-from-SEAsia/list/62128)")
    col1.markdown("- [Games from Indonesia (Part 1)](https://store.steampowered.com/curator/25278687-Virtual-SEA-Games-from-SEAsia/list/37980)")
    col1.markdown("- [Daftar Game Buatan Developer Indonesia di Steam](https://steamcommunity.com/groups/indosteamcommunity/discussions/1/1486613649676936297?ctp=14)")
    col1.markdown("- [Steam wiki](https://en.wikipedia.org/wiki/Steam_(service))")
    col2.markdown("- [Akses Steam sudah dibuka kembali per 2 Agustus 2022](https://gamerwk.com/steam-sudah-bisa-diakses-di-indonesia-kominfo-lepas-blokir/)")
    col2.markdown("- [Komfino blokir Steam dan Paypal hingga menjadi trending Twitter](https://www.detik.com/bali/berita/d-6207923/steam-paypal-diblokir-tagar-blokirkominfo-trending-twitter)")
    col2.markdown("- [Kominfo sudah kirim surat teguran 23 Juli 2022](https://tekno.kompas.com/read/2022/07/29/16450017/batas-pendaftaran-pse-nanti-malam-platform-digital-yang-bandel-akan-diblokir)")
    col2.markdown("- [Whatsapp, FB, Instagram sudah daftar PSE; tidak jadi diblokir](https://www.cnbcindonesia.com/tech/20220720073311-37-356882/whatsapp-fb-instagram-sudah-daftar-kominfo-ga-jadi-diblokir)")
    col2.markdown("- [Isu pemblokiran sebelumnya untuk Google hingga Whatsapp](https://www.cnnindonesia.com/teknologi/20220622152237-192-812237/akses-google-hingga-whatsapp-bisa-diputus-jika-tak-daftar-pse-kominfo)")
    col2.markdown("- [Pendaftaran PSE sudah dibuka sejak 2 Juni 2021](https://aptika.kominfo.go.id/2021/05/ketentuan-pse-lingkup-privat-untuk-lindungi-negara-dan-masyarakat/)")
    col2.markdown("- [Aturan PSE (2020) didasarkan pada UU ITE](https://aptika.kominfo.go.id/2020/01/pendaftaran-penyelenggara-sistem-elektronik-pse/)")
