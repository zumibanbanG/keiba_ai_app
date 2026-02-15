import streamlit as st
from google.cloud import run_v2

# 競馬場IDと名称
PLACES = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京", "08": "京都",
    "09": "阪神", "10": "小倉"
}
JOB_NAME = "projects/keiba-ai-487108/locations/us-central1/jobs/keiba-collector"

st.title("Keiba Collector ジョブ実行")

# 年度選択
year = st.selectbox("年度を選択", options=[str(y) for y in range(2015, 2027)], index=11)

# 馬場選択
place_options = ["全て"] + [f"{v}({k})" for k, v in PLACES.items()]
place = st.selectbox("馬場を選択", options=place_options)

run = st.button("Cloud Run Jobs 実行")

if run:

    client = run_v2.JobsClient()

    if not year:
        st.error("年度は必須です")
    else:
        results = []
        place_ids = list(PLACES.keys()) if place == "全て" else [place.split("(")[-1].replace(")", "")]
        for place_id in place_ids:
            envs = {"YEAR": year, "PLACE_ID": place_id}
            request = run_v2.RunJobRequest(
                name=JOB_NAME,
                overrides=run_v2.types.RunJobRequest.Overrides(
                    container_overrides=[
                        run_v2.types.RunJobRequest.Overrides.ContainerOverride(
                            env=[run_v2.types.EnvVar(name=k, value=v) for k, v in envs.items()]
                        )
                    ],
                )
            )
            try:
                operation = client.run_job(request=request)
                results.append(f"{PLACES[place_id]}({place_id}): ジョブ実行開始 (operation: {operation.operation.name})")
            except Exception as e:
                results.append(f"{PLACES[place_id]}({place_id}): 実行エラー {e}")
        st.write("## 実行結果")
        for r in results:
            st.write(r)
