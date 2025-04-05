import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Сервіс для завантаження файлів у Cloudinary.

    Attributes:
        cloud_name (str): Назва хмари Cloudinary
        api_key (str): Ключ API Cloudinary
        api_secret (str): Секретний ключ API Cloudinary
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Ініціалізація сервісу завантаження файлів.

        Args:
            cloud_name (str): Назва хмари Cloudinary
            api_key (str): Ключ API Cloudinary
            api_secret (str): Секретний ключ API Cloudinary
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантаження файлу в Cloudinary.

        Args:
            file: Файл для завантаження
            username (str): Ім'я користувача для формування public_id

        Returns:
            str: URL завантаженого зображення

        Note:
            Зображення буде автоматично обрізане до розміру 250x250 пікселів
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
