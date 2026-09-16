# LogiSense-AI: A Leakage-Safe Machine Learning Framework for Pre-Fulfillment Supply Chain Delay Risk Forecasting

[**Author / Research Team]**  
**Affiliation:** LogiSense-AI Platform & Research Group  
**Repository:** https://github.com/pika1063/LogiSense-AI  
**Date:** September 2026  

---

## Abstract
Accurate prediction of supply chain delivery delays prior to order dispatch is critical for operational resilience and customer satisfaction. However, existing logistics machine learning implementations frequently suffer from **target leakage** by incorporating post-fulfillment artifacts (e.g., realized transit times, updated order lifecycle statuses, or realized profit margins), inflating experimental benchmark results while failing catastrophically in production. In this paper, we propose **LogiSense-AI**, a full-stack, leakage-safe machine learning platform engineered to forecast binary delivery delay risk (`Late_delivery_risk`, 0 = on-time, 1 = late) strictly utilizing attributes knowable at booking time. Evaluated on 172,765 real-world delivery records from the APLLogistics dataset, our tuned Random Forest model achieves an **F1-Score of 69.08%**, a **ROC-AUC of 75.47%**, and an **Accuracy of 69.21%** across 136 one-hot encoded and scaled feature dimensions. We present the end-to-end architecture, mathematical methodology, explainability insights, and containerized deployment infrastructure.

