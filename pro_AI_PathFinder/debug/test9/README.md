置顶
1.笔记本上python的编辑器路径和工具包路径。
C:\Users\xiejun4\AppData\Local\Microsoft\WindowsApps\python3.12.exe
c:\users\xiejun4\appdata\local\packages\pythonsoftwarefoundation.python.3.12_qbz5n2kfra8p0\localcache\local-packages\python312\site-packages


2025-09-04
1.在trae中调试html文件
    1.在powershell中启动http服务器
    D:\PythonProject\pro_PathFinder\debug\test9\docs> D:\anaconda3\python.exe -m http.server 8000
   公司：
    cd 'D:\PythonProject\pro_PathFinder\debug\test9\docs'; D:\anaconda3\python.exe -m http.server 8000 
   家里：
    cd 'D:\ProgramData\projects\pro_PathFinder\debug\test9\docs'; D:\ProgramData\anaconda3\python.exe -m http.server 8000  

    2.在浏览器中打开http://localhost:8000/json_viewer.html
    3.python脚本目录：/debug/test9/json_viewer.html

2025-09-16
问题：页面一直无法铺满整个页面。
解决：
让我检查服务器状态以确保一切正常运行：
经过分析和修改，我已经解决了container容器无法铺满整个页面的问题。以下是我所做的修改：

1. 1.
   首先，我检查了.container类的CSS样式，发现虽然设置了width: 100%和height: 100vh，但可能受到浏览器默认样式或其他因素影响。
2. 2.
   我对.container类进行了以下优化：
   
   - 将width: 100%改为width: 100vw，确保使用视口宽度单位
   - 添加了min-height: 100vh和min-width: 100vw，确保容器至少占据整个视口
   - 添加了overflow: hidden，防止内容溢出影响布局
3. 3.
   同时，我也优化了body的样式：
   
   - 添加了width: 100vw，确保body占据整个视口宽度
   - 设置margin: 0和padding: 0，消除浏览器默认的边距
这些修改确保了.container容器能够完全铺满整个页面，消除了任何可能导致布局问题的边距或填充。现在页面应该能够正确地占据整个浏览器窗口。


2025-9-19
在添加数据页面中，这两个按钮的作用如下：

1. 1.
   保存到内存 ：
   
   - 这是表单的默认提交按钮
   - 当您点击此按钮时，数据会被保存到浏览器的本地存储（localStorage）中
   - 这意味着数据会在您的浏览器中持久化存储，即使您关闭页面或刷新页面，数据依然存在
   - 数据仅保存在您当前使用的浏览器中，不会保存到任何文件或服务器上
2. 2.
   保存到文件 ：
   
   - 这是一个单独的按钮，点击后会触发文件下载功能
   - 它会将当前所有的数据（包括您刚刚添加的数据）保存为一个JSON文件并下载到您的计算机上
   - 这样您可以将数据备份到本地磁盘，或者在其他设备上使用
   - 如果您之前通过文件选择功能加载了一个JSON文件，点击此按钮时会使用相同的文件名进行保存
在实际使用中：

- 如果您只是想临时保存数据并在当前浏览器中使用，点击"保存到内存"即可
- 如果您想将数据备份或导出到本地文件系统，可以点击"保存到文件"按钮
需要注意的是，如果您之前通过"选择文件"按钮加载了JSON文件，那么在保存时会自动使用该文件名进行保存。如果没有加载过文件，则需要先选择一个文件才能使用"保存到文件"功能。

### localStorage 的特性
1. 1.
   持久性存储 ：
   
   - localStorage 是一种持久化存储机制，数据保存在用户的本地磁盘上
   - 即使电脑重启或浏览器关闭，数据也不会丢失
   - 数据会在同域下永久保存，直到用户手动清除或通过代码删除
2. 2.
   与内存存储的区别 ：
   
   - 内存存储（如 JavaScript 变量）在页面关闭或刷新后会丢失
   - localStorage 是磁盘存储

用户5053084991

复制

删除

localStorage 的数据存储位置 ： localStorage 是浏览器提供的一种 持久化存储机制 ，数据保存在用户的本地磁盘上，那是在本地磁盘的那个具体的文件目录中？

Builder

关于您的问题， localStorage 的数据存储位置取决于用户使用的浏览器类型和操作系统。重要的是要知道 localStorage 是由浏览器管理的，而不是由网站或网页应用直接管理的。以下是不同浏览器在不同操作系统上的 localStorage 存储位置：

### Windows 系统：
1. 1.
   Google Chrome ：
   
   - C:\Users\[用户名]\AppData\Local\Google\Chrome\User Data\Default\Local Storage\
2. 2.
   Mozilla Firefox ：
   
   - C:\Users\[用户名]\AppData\Roaming\Mozilla\Firefox\Profiles\[随机字符串].default\storage\default\
3. 3.
   Microsoft Edge ：
   
   - C:\Users\[用户名]\AppData\Local\Microsoft\Edge\User Data\Default\Local Storage\
4. 4.
   Internet Explorer ：
   
   - C:\Users\[用户名]\AppData\Local\Microsoft\Internet Explorer\DOMStore\



       <script src="../js/chart.min.js"></script>

2025-9-21
1. 
当加载某个产品的L2Vision异常日志之后，
如果异常测试项在JOTSLIM+L2VISION_grouped_output_with_properties.json中不存在，
工具将异常测试项名和异常log加入JOTSLIM+L2VISION_grouped_output_with_properties.json中，json_viewer.html上显示（测试项：异常测试项名，状态：待加入），
然后通知负责人手动完善。
