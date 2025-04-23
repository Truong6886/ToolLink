<h3>Xây dựng giao diện trực quan hoá, dự báo, dự đoán giá cổ phiếu ngân hàng VCB</h3>
<h1 align="center">
 
  <img src="/images/giao_dien_chinh.png" alt="Markdownify" width="1000">
</h1>
 <i  align="center">Giao diện chính trang web.</i>

## Chức năng <br>
Trang web có 7 chức năng: <br>
 + Load Data(Load dữ liệu) <br>
 + Missing Values(dữ liệu bị mất) <br>
 +  Choose distribution(chọn phân phối thuộc tính) <br>
 +  Year-Wise Time Series Plot(chọn vẽ biểu đồ chuỗi thời gian theo năm) <br>
 +  Technical Indicators(chọn các chỉ báo kỹ thuật) <br>
 +  Choose Forecasting Model(chọn loại dự báo) <br>
 +  Choose Machine Learning Model(chọn loại dự đoán)<br>
## Cách dùng: <br>
Ở trang chủ người dùng sẽ thấy được thông tin của trang web. Phần danh mục bên trái sẽ là các chức năng chính của trang web. <br>
<strong> Load data </strong> <br>
Khi chọn vào nút Load Data thì bên phải sẽ hiển thị tải dữ liệu giá cổ phiếu VCB. <br>
<br>
<img src="/images/load_data.png" alt="" width="1000">
<i  align="center">Giao diện Load Data.</i> <br>

<strong> Missing Values </strong> <br>
Khi chọn vào nút Missing Values bên phải sẽ hiển thị biểu đồ biểu đồ cột biểu diễn số lượng giá trị dữ liệu bị mất(missing values).<br>
<br>
<img src="/images/missing_values.png" alt="" width="1000">
<i  align="center">Giao diện Missing Values.</i> <br>
<strong> Correlation Coefficient </strong> <br> Khi chọn vào nút Correlation Coefficient, bên phải hiển thị biểu đồ cột thể hiện hệ số tương quan (correlation coefficient) giữa các thuộc tính (features) và cột giá đóng cửa điều chỉnh (Adj Close). <br>
<br>
<img src="/images/correlation_cofficient.png" alt="" width="1000">
<i  align="center">Giao diện Correlation Coefficient.</i> <br>

<strong> Choose distribution </strong> <br> 
Khi chọn một thuộc tính từ danh sách bên trái trong Choose distribution bên phải sẽ hiển thị biểu đồ phân phối của thuộc tính bao gồm <br>
 + Day <br>
 + Month <br>
 + Quarter <br>
 + Year <br>
 + Open versus Adj Close versus Year <br>
 + Low versus High versus Quarter <br>
 + Adj Close versus Volume versus Month <br>
 + High versus Volume by Day <br>
 + The distribution of Volume by Year <br>
 + The distribution of Volume by Month <br>
 + The distribution of Volume by Day <br>
 + The distribution of Volume by Quarter <br>
 + Year versus Categorized Volume <br>
 + Day versus Categorized Volume <br>
 + Month versus Categorized Volume<br>
 + Quarter versus Categorized Volume <br>
 + Categorized Volume <br>
 + Correlation Matrix <br>
      
 <strong> Year-Wise Time Series Plot </strong> <br> Khi chọn một thuộc tính từ danh sách bên trái trong Year-Wise Time Series Plot (chọn vẽ biểu đồ chuỗi thời gian theo năm) bên phải sẽ hiển thị biểu đồ dữ liệu theo năm bao gồm các thuộc tính <br>
   + Low and High <br>
   + Open and Close <br>
   + Adj Close and Close <br>
   + Year Wise Mean and EWM of Low and High <br>
   + Year Wise Mean and EWM of Open and Close <br>
   + Normalized Year-Wise Data  <br>
   
<strong> Technical Indicators </strong>  <br> 
	Khi chọn một thuộc tính từ danh sách bên trái trong Technical Indicators(chọn các chỉ báo kỹ thuật) bên phải sẽ hiển thị biểu đồ liên quan đến chỉ báo kỹ thuật như
  + Adj Close versus Daily Return by Year  <br>
  +  Volume versus Daily Return by Quarter  <br>
  +  Low versus Daily Return by Month  <br>
  +  High versus Daily Return by Day, Technical Indicator  <br>
  + Differences <br>
  
 <strong> Choose Forecasting Model </strong>  <br>
Khi chọn một thuộc tính từ danh sách bên trái trong Choose Forecasting Model (chọn loại dự báo)  bên phải sẽ hiển thị biểu đồ và thông tin liên quan đến dự báo bao gồm
   + Linear Regression <br>
   + Lasso Regression <br>

  <strong> Choose Machine Learning Model </strong>  <br>
Khi chọn một thuộc tính từ danh sách bên trái trong Choose Machine Learning Model (chọn loại dự đoán) bên phải sẽ hiển thị biểu đồ và thông tin liên quan đến dự đoán.<br>
+ Linear Regression  Support Vector Machine (SVC) <br>
+ Logistic Regression)



## Website
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vcb-gui.streamlit.app/)

## Thư viện sử dụng 
<img src="https://user-images.githubusercontent.com/7164864/217935870-c0bc60a3-6fc0-4047-b011-7b4c59488c91.png" alt="Streamlit logo" style="margin-top:50px"></img>
<h3>Streamlit</h3>


## 📝 License

MIT

---

