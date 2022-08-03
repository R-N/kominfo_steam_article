import streamlit as st
import pandas as pd
from ..functions.twitter import POLARITY_LABEL_VOLUME_COLS as TWITTER_POLARITY_LABEL_VOLUME_COLS, QUERIES as TWITTER_QUERIES, EXCLUDE_QUERIES as TWITTER_EXCLUDE_QUERIES, POLARITY_LABEL_COLS as TWITTER_POLARITY_LABEL_COLS, LABELS as TWITTER_LABELS, INCLUDE_QUERIES as TWITTER_INCLUDE_QUERIES, DATES as TWITTER_DATES
from ..functions.twitter import load_all as twitter_load_all, aggregate_data as twitter_aggregate_data, filter_query as twitter_filter_query, merge_data as twitter_merge_data
from ..display.twitter import tweet_volume_bar_stack, tweet_slides, display_tweet
from ..display.steam import game_bar_horizontal, game_scatter, show_metrics as steam_show_metrics, game_histogram
from ..global_data import Constants
from ..functions.steam import LABELS as STEAM_LABELS
from ..functions.gtrends import LABELS as GTRENDS_LABELS, DEFAULT_COLS_1 as GTRENDS_DEFAULT_COLS_1
from ..functions.gtrends import load_df as gtrends_load_df
from ..display.gtrends import trend_line
from ..display.util import selectbox_2, multiselect_2
from ..functions.steam import split_by_availability as steam_split_by_availabiltiy, init_df as steam_init_df, groupby_tag_2 as steam_groupby_tag_2, limit_df as steam_limit_df
import json

container_type = type(st.container)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def tweet_section(container, all_data, sentiment="all", queries=TWITTER_INCLUDE_QUERIES, dates=TWITTER_DATES, sorting="engagement", limit=10):
    con1 = container.container()
    con2 = container.container()
    if container.checkbox("Filter"):
        sentiment = selectbox_2(
        container,
        "Sentimen",
        {
            k: TWITTER_LABELS[k]
            for k in [
                "positive",
                "neutral",
                "negative",
                "all"
            ]
        },
        default=sentiment
    )
        queries = multiselect_2(
            container, 
            "Query", 
            {k:k for k in queries}, 
            default=queries
        )
        dates = multiselect_2(
            container, 
            "Tanggal", 
            {k:k for k in dates}, 
            default=dates
        )
    merged = twitter_merge_data(all_data, queries, dates)
    if sentiment != "all":
        merged = merged[merged["sentiment_label"]==TWITTER_LABELS[sentiment]]
    col1, col2, col3 = con1.columns(3)
    sorting = selectbox_2(
        col2,
        "Sort by",
        {
            k: TWITTER_LABELS[k]
            for k in [
                "like_count",
                "reply_count",
                "retweet_count",
                "quote_count",
                "engagement"
            ]
        },
        default=sorting
    )
    limit = col3.number_input(
        "Limit",
        min_value=0,
        max_value=100,
        value=limit,
        step=1
    )
    merged = merged.sort_values(sorting, ascending=False).iloc[:int(limit)].reset_index()
    #st.dataframe(merged)
    tweets = merged.to_dict('records')
    #st.write(tweets)
    max_index = len(tweets)-1
    index = col1.number_input(
        "Tweet #",
        min_value=0,
        max_value=max_index,
        value=0,
        step=1
    )
    index = int(index)
    #tweet_slides(con2, tweets, key="twitter")
    
    tweet = tweets[index]
    display_tweet(con2, tweet, "Top Tweet #{0}".format(index+1))

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def gtrends_section(container, sheet="indo_hourly", labels=GTRENDS_LABELS, whitelist=GTRENDS_DEFAULT_COLS_1, key="trends1"):
    if container.checkbox("Opsi", key=key):
        sheet = selectbox_2(container, "Google Trends", labels, default="indo_hourly")
    df = gtrends_load_df(sheet)
    trend_line(container, df, whitelist=whitelist)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def tweet_sentiment_section(container, aggregate, query="kominfo", labels=TWITTER_POLARITY_LABEL_VOLUME_COLS, key="sentiment"):
    
    if container.checkbox("Opsi", key=key):
        query = selectbox_2(
            container, 
            "Query", 
            {k:k for k in TWITTER_QUERIES if k not in TWITTER_EXCLUDE_QUERIES}, 
            default="kominfo",
            key=key
        )
        volume = selectbox_2(container, "Volume", {
            "volume": "Dikali like/rt",
            "count": "Hanya jumlah"
        }, default="volume", key=key)
        labels = TWITTER_POLARITY_LABEL_VOLUME_COLS if volume=="volume" else TWITTER_POLARITY_LABEL_COLS

    df_q = twitter_filter_query(aggregate, query)
    con = container.container()
    tweet_volume_bar_stack(con, df_q, labels)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def tweet_volume_section(container, aggregate, query="kominfo", count="count_rt", key="volume"):
    if container.checkbox("Opsi", key=key):
        query = selectbox_2(
            container, 
            "Query", 
            {k:k for k in TWITTER_QUERIES if k not in TWITTER_EXCLUDE_QUERIES}, 
            default="kominfo",
            key=key
        )
        count = selectbox_2(container, "Jumlah", {
            "count": "Hanya tweet original",
            "count_rt": "Tweet + Retweet",
            "count_rt_quote": "Tweet + Retweet + Quote"
        }, default="count_rt", key=key)
    df_q = twitter_filter_query(aggregate, query)
    con = container.container()
    tweet_volume_bar_stack(con, df_q, count)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def steam_histogram_section(container, df, key="default"):
    col = selectbox_2(container, "x", {
        x: STEAM_LABELS[x] for x in [
            "price_initial",
            "total_reviews",
            "total_positive",
            "estimated_revenue",
            "estimated_revenue_positive"
        ] if x in df.columns
    }, default="estimated_revenue_positive", key=key)
    df, limit = steam_limit_df(container, df, col, key=key)
    steam_show_metrics(container, df[col], 1)
    game_histogram(container, df, col)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def steam_scatter_section(container, df, key="default"):
    col1, col2 = container.columns(2)
    x = selectbox_2(col1, "x", {
        x: STEAM_LABELS[x] for x in [
            "price_initial",
            "total_reviews",
            "total_positive",
            "release_date"
        ] if x in df.columns
    }, default="price_initial", key=key)
    y = selectbox_2(col2, "y", {
        x: STEAM_LABELS[x] for x in [
            "price_initial",
            "total_reviews",
            "total_positive",
            "release_date",
            "estimated_revenue",
            "estimated_revenue_positive",
        ] if x in df.columns
    }, default="total_positive", key=key)
    zs = multiselect_2(container, "z", {
        x: STEAM_LABELS[x] for x in [
            "total_reviews",
            "total_positive",
            "estimated_revenue",
            "estimated_revenue_positive",
            "developers",
            "publishers"
        ] if x in df.columns
    }, default=[
        "estimated_revenue",
        "estimated_revenue_positive",
        "review_summary",
        "developers",
        "publishers"
    ], key=key)

    game_scatter(container, df, x, y, zs)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, container_type: id})
def steam_bar_horizontal_section(container, df, key="default"):
    col1, col2 = container.columns(2)
    x = selectbox_2(col1, "x", {
        x: STEAM_LABELS[x] for x in [
            "price_initial",
            "total_reviews",
            "total_positive",
            "estimated_revenue",
            "estimated_revenue_positive",
            "count"
        ] if x in df.columns
    }, default="total_positive", key=key)
    y = selectbox_2(col2, "y", {
        x: STEAM_LABELS[x] for x in [
            "genres",
            "categories",
            "platforms",
            "supported_languages",
            "supported_languages_voice"
        ] if x in df.columns
    }, default="genres", key=key)
    agg_cb = container.checkbox("Agg", value=True, key=key)
    con = container.container()
    game_bar_horizontal(
        con, df, x, y, 
        agg=agg_cb
    )

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

    st.markdown("# Steam, Pintu Ekspor Terbesar Industri Game Indonesia yang Ditutup oleh Kominfo")

    col1, col2 = st.columns((1, 1))
    col2.image("assets/letmein steam.png")
    col2.caption("Insiden pemblokiran Steam oleh Kominfo, circa 2022, memeized")

    col1.image("assets/blokirkominfo.png")
    col1.markdown("Hari Sabtu tanggal 30 Juli 2022 lalu, terkait aturan PSE, Kemenkominfo telah memblokir beberapa layanan besar dari luar negeri, salah satunya Steam. Pemblokiran ini menghebohkan media internet Indonesia dan langsung menjadi trending twitter. Sebagian besar tweet masih netral dan positif, tapi jumlah tweet negatif juga sangat banyak. Bagaimana tidak, setelah melalui 5 hari kerja yang panjang, orang-orang Indonesia ternyata tidak dapat refreshing dengan game yang telah dibeli; semua karena suatu regulasi baru dari pemerintah. Bukan cuma tempat membeli game, Steam juga adalah pintu ekspor terbesar industri game Indonesia. Developer Indonesia diestimasikan telah meraup sebanyak 1,66 miliar rupiah, dimana 1,58 miliar rupiah di antaranya berasal dari game indie. Developer game indie tidak memiliki sponsor besar dalam pembuatannya, dan industri game di Indonesia sendiri terbilang kecil, tapi Steam memungkinkan mereka menjual ke seluruh dunia. Sepenting itu lah Steam bagi industri dan pasar game Indonesia. Untungnya, per tanggal 2 Agustus 2022, akses Steam telah dibuka kembali.")

    st.markdown("## Trending Twitter dan Kronologi")

    col1, col2 = st.columns((2, 3))

    col1.markdown("Tanggal 30 Juli 2022, Kominfo langsung melesat ke puncak trending Twitter untuk Indonesia hingga lebih dari 40 ribu tweet. Angka ini tidak termasuk retweet, dan jika retweet dihitung akan mencapai lebih dari 240 ribu tweet. Pemblokiran yang menyebabkan kehebohan ini dilakukan karena aturan PSE, dimana setiap penyelenggara sistem elektronik wajib mendaftar dan memenuhi aturan yang berlaku. Wacana pemblokiran PSE ini sudah dari dua minggu sebelumnya dengan Google, Whatsapp, dan Instagram sebagai topik, tapi pada akhirnya mereka telah mendaftar dan topik PSE mulai surut. Dua, tiga hari berlalu, masih tidak terjadi apa-apa; ancaman pemblokiran seperti ancaman kosong. Ternyata Kominfo tidak langsung melakukan pemblokiran, tapi memberi surat teguran dan memperpanjang batas pendaftaran hingga satu minggu setelahnya. Ini dilakukan pada tanggal 23 Juli 2022. Karena tidak kunjung mendaftar, beberapa layanan besar akhirnya diblokir. Meskipun sebagian besar tweet masih netral dan positif, pemblokiran ini menuai banyak sekali respon negatif.")

    tab_sentiment, tab_volume, tab_gtrends = col2.tabs(["Sentimen", "Volume", "Google Trends"])
    tweet_sentiment_section(tab_sentiment, aggregate)
    tweet_volume_section(tab_volume, aggregate)
    gtrends_section(tab_gtrends)

    tweet_section(st, all_data)

    st.markdown("## Steam dan Game Indonesia")

    col1, col2 = st.columns((1, 1))
    col2.image("assets/steam industri.jpg")
    col2.caption("dan kenapa pendapatan pajak barang digital turun")

    col1.markdown("Steam adalah salah satu layanan yang diblokir tanggal 30 Juli lalu. Steam adalah sebuah marketplace game terbesar di dunia untuk PC. Steam juga adalah pintu ekspor terbesar industri game Indonesia. Developer Indonesia diestimasikan telah meraup sebanyak 1,66 miliar rupiah, dimana penjualan terbesar 437,3 juta rupiah oleh Toge Productions dengan Coffee Talk, sebuah game indie. Developer game indie tidak memiliki sponsor besar dalam pembuatannya, dan industri game di Indonesia sendiri terbilang kecil, tapi Steam memungkinkan mereka menjual ke seluruh dunia. Sebesar 1,58 miliar rupiah dari 1,66 miliar rupiah tadi didapat oleh game indie.")
    col1.markdown("Game Indonesia di Steam didominasi oleh genre adventure, casual, dan action, tapi kalau dilihat dari popularitas, genre adventure jauh meninggalkan yang lain. Sebagian besar game Indonesia merupakan game single-player dengan fitur steam achievement, steam cloud, dan steam trading cards. Semua game Indonesia mendukung bahasa Inggris, tapi game-game populer juga mendukung bahasa lain seperti bahasa Cina, Jepang, Spanyol, Rusia, Jerman, Portugis-Brazil, Prancis hingga Korea. Anehnya, tidak ditemukan bahasa Indonesia. Apa memang tidak ada atau hanya tag-nya saja yang tidak ada? Masih mengenai bahasa; sebagian besar game Indonesia tidak mendukung suara, tapi yang mendukung suara bahasa Inggris tidak kalah banyak.")


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
    
    st.markdown("Memang tidak sedikit game Indonesia yang telah berhasil di Steam. Meskipun begitu, tidak mudah untuk membuat game yang sukses. Dari 132 game Indonesia yang telah rilis dan masih ada di Steam, sekitar setengahnya diestimasikan hanya menjual sekitar satu juta rupiah (median 1.16 juta). Hanya 23 dari 132 game ini yang berhasil menjual lebih dari 10 juta rupiah. Padahal, waktu, tenaga, dan uang yang diperlukan untuk mengembangkan game cukup besar, sedangkan developer indie sulit mencari dana. Perlu mental yang kuat dan persiapan yang matang jika memang ingin berkarir di industri game Indonesia. Industri yang sudah sulit ini akan jadi jauh lebih sulit lagi jika Steam benar-benar diblokir.")

    st.markdown("## Bypass Blokir")
    col1, col2 = st.columns((1, 1))
    col2.image("assets/Lah green tunnel.png")
    #col2.caption("hehe")
    col1.markdown("Untungnya, akses ke Steam telah dibuka kembali per tanggal 2 Agustus 2022. Namun, jika lagi-lagi aturan PSE memblokir suatu layanan penting, kalian bisa gunakan salah satu aplikasi ini:")
    col1.markdown("- [Green Tunnel (Windows, Linux, MacOS)](https://github.com/SadeghHayeri/GreenTunnel)")
    col1.markdown("- [DPITunnel v2 (Linux & Android, perlu root)](https://github.com/zhenyolka/DPITunnel-android)")
    col1.markdown("- [PowerTunnel (Windows & Android)](https://github.com/krlvm/PowerTunnel)")
    col1.markdown("Meskipun ada cara bypass pemblokiran, ini hanya solusi sementara. Jika benar-benar diblokir permanen, suatu layanan akan menjadi ilegal. Ini berarti meskipun kita bisa bypass blokir, pemberi layanan tidak dapat mendukung Indonesia. Contohnya, kalian akan kesulitan untuk topup dengan rupiah.")

    st.markdown("## Referensi")
    st.markdown("- [Nanti ya](#)")