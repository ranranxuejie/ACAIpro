# 文件工具模块 - 处理文件显示和样式

# 定义文件图标映射
FILE_ICONS = {
    # 文档类
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'txt': '📄',
    'md': '📄',
    'rtf': '📄',
    # 表格类
    'xls': '📊',
    'xlsx': '📊',
    'csv': '📊',
    'tsv': '📊',
    # 代码类
    'py': '🐍',
    'java': '☕',
    'cpp': '++',
    'c': '📟',
    'h': '📟',
    'js': '🟨',
    'ts': '🔷',
    'html': '🌐',
    'css': '🎨',
    'json': '📋',
    'xml': '📋',
    # 图片类
    'jpg': '🖼️',
    'jpeg': '🖼️',
    'png': '🖼️',
    'gif': '🎞️',
    'svg': '🎨',
    'bmp': '🖼️',
    # 视频类
    'mp4': '🎬',
    'avi': '🎬',
    'mov': '🎬',
    'wmv': '🎬',
    'flv': '🎬',
    # 音频类
    'mp3': '🎵',
    'wav': '🎵',
    'ogg': '🎵',
    'flac': '🎵',
    # 压缩文件类
    'zip': '🗜️',
    'rar': '🗜️',
    '7z': '🗜️',
    'tar': '🗜️',
    'gz': '🗜️',
    # 其他
    'exe': '⚙️',
    'dll': '⚙️',
    'bin': '⚙️',
    'iso': '💿',
}


def get_file_icon(file_name):
    """
    根据文件名获取对应的文件图标
    
    Args:
        file_name (str): 文件名
        
    Returns:
        str: 文件图标
    """
    if '.' in file_name:
        ext = file_name.split('.')[-1].lower()
        return FILE_ICONS.get(ext, '📦')
    return '📦'


def format_file_attachment(file_name, file_url):
    """
    格式化单个文件附件为HTML样式
    
    Args:
        file_name (str): 文件名
        file_url (str): 文件URL
        
    Returns:
        str: 格式化后的HTML
    """
    icon = get_file_icon(file_name)
    return f"<div style='display: inline-block; background-color: #f0f2f6; padding: 6px 12px; border-radius: 8px; margin-right: 8px; margin-bottom: 4px;'><span>{icon}</span> <a href='{file_url}' target='_blank' style='text-decoration: none; color: #1a73e8; font-weight: 500;'>{file_name}</a></div>"


def format_file_attachments(files, file_name=None, file_url=None):
    """
    格式化多个文件附件为HTML样式
    
    Args:
        files (list): 文件列表，每个文件包含name和url
        file_name (str, optional): 单个文件名（兼容旧数据）
        file_url (str, optional): 单个文件URL（兼容旧数据）
        
    Returns:
        str: 格式化后的HTML
    """
    file_htmls = []
    
    # 处理files属性
    if files:
        for file in files:
            file_name_item = file.get('name', '')
            file_url_item = file.get('url', '#')
            if file_name_item:
                file_htmls.append(format_file_attachment(file_name_item, file_url_item))
    
    # 处理file_name属性（兼容旧数据）
    if file_name and file_name not in [file.get('name') for file in files or []]:
        file_htmls.append(format_file_attachment(file_name, file_url or '#'))
    
    return ''.join(file_htmls)


def integrate_files_into_content(content, files, file_name=None, file_url=None):
    """
    将文件附件集成到内容中
    
    Args:
        content (str): 原始内容
        files (list): 文件列表
        file_name (str, optional): 单个文件名
        file_url (str, optional): 单个文件URL
        
    Returns:
        str: 集成了文件的内容
    """
    file_html = format_file_attachments(files, file_name, file_url)
    if file_html:
        # 在文件附件后面添加更多换行，增加与正文的间隔
        return f"{file_html}\n\n\n{content}"
    return content
