# 易教帮简易操作流程


1. 设置工作目录，工作目录下需要有一个“**学生信息表.csv**”，可以从附件中直接获得。操作如下
   - 新建文件夹，名字任意。
   - 把附件中的“**学生信息表.csv**”复制到新的文件夹下
   - 点击UI界面的“**工作目录**”，选择刚刚新建的文件夹
   - 这时，系统会提示缺失某些目录，选择是，自动创建
2. 设置作业编号。

   - 点击UI界面的“**作业批次**”
   - 弹出对话框，输入一个整数。这里可以直接用默认值1，直接确定
   - 此时又会提示缺失某些目录，选择是，自动创建
   - 还会提示找不到“**作业统计信息表.csv**”，选择是，自动创建
3. 这样，环境就搭建完毕了。
4. 接下来模拟收作业的过程。假设助教获得一批作业，现在需要助教手动把作业放到自动创建的“**待归档作业**”文件夹下。附件中已经提供了测试用的空作业

   - 把附件中的所有作业复制到“**待归档作业**”文件夹下。

     - 注意，不是复制作业所在的文件夹。也就是说，“**待归档作业**”文件夹应当直接是作业文件
   - 点击UI界面的“**作业归档**”

     - 该操作会把“**待归档作业**”文件夹下的文件移动到“**已归档作业**”，并根据“**学生信息表.csv**”规范命名作业文件
5. 最后由助教为每个作业评分。

   - 点击UI界面的“**作业批改**”
   - 输入学号

     - 若学号输入错误会报错
   - 输入成绩
   - 输入批注（可以为空）
   - 该系统会将对应文件移动到“**已批改作业**”，并把相应信息填入“**作业统计信息表.csv**”
6. 显然，系统重启后，数据不会丢失，因为已经写入磁盘。

   - 若重启系统，需要重新设置工作路径（beta发布时可能会简化此操作），重新设置作业批次
   - 但是如果“**待归档作业**”等相关文件夹已经存在，不会覆盖。如果“**作业统计信息表.csv**”已经存在，不会重建。环境的搭建是自动检测，动态变化的。
   - 因此，该系统可以随时启动，随时关闭。

