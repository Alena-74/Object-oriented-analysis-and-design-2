using System;

namespace TeatralnayaPostanovka
{
    public class Suits
    {
        public string Type;
        public string Color;
        public string Material;

        public void ShowInfo()
        {
            Console.WriteLine($"костюмы: {Type}, цвет {Color}, материал {Material}");
        }
    }

    public class Scene
    {
        public string Type;
        public string Color;
        public string Material;

        public void ShowInfo()
        {
            Console.WriteLine($"декорации: {Type}, цвет {Color}, материал {Material}");
        }
    }

    public class Acting
    {
        public string Type;
        public string Style;
        public string Emotions;

        public void ShowInfo()
        {
            Console.WriteLine($"актерская игра: {Type}, стиль {Style}, эмоции {Emotions}");
        }
    }

    public class Director
    {
        public Suits CurrentSuits;
        public Scene CurrentScene;
        public Acting CurrentActing;

        public void CreateDrama()
        {
            CurrentSuits = new Suits
            { 
                Type = "драматические", Color = "приглушенные", Material = "натуральные" 
            };
            CurrentScene = new Scene 
            { 
                Type = "драматические", Color = "темные", Material = "дерево" 
            };
            CurrentActing = new Acting
            { 
                Type = "драматическая", Style = "психологический", Emotions = "глубокие" 
            };
            Console.WriteLine("создана драма");
        }

        public void CreateComedy()
        {
            CurrentSuits = new Suits 
            { 
                Type = "комедийные", Color = "яркие", Material = "синтетика" 
            };
            CurrentScene = new Scene 
            { 
                Type = "комедийные", Color = "красочные", Material = "картон" 
            };
            CurrentActing = new Acting 
            { 
                Type = "комедийная", Style = "гротеск", Emotions = "преувеличенные"
            };
            Console.WriteLine("создана комедия");
        }

        public void CreateMusical()
        {
            CurrentSuits = new Suits 
            { 
                Type = "мюзикловые", Color = "блестящие", Material = "пайетки" 
            };
            CurrentScene = new Scene 
            {
                Type = "мюзикловые", Color = "золотые", Material = "металл" 
            };
            CurrentActing = new Acting
            { 
                Type = "мюзикловая", Style = "вокально-хореографический", Emotions = "радостные"
            };
            Console.WriteLine("создан мюзикл");
        }

        public void ShowCurrent()
        {
            Console.WriteLine();
            Console.WriteLine("текущий спектакль");
            CurrentSuits?.ShowInfo();
            CurrentScene?.ShowInfo();
            CurrentActing?.ShowInfo();
            Console.WriteLine();
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Director director = new Director();

            director.CreateDrama();
            director.ShowCurrent();

            director.CreateComedy();
            director.ShowCurrent();

            director.CreateMusical();
            director.ShowCurrent();

            Console.WriteLine("\nнажмите любую клавишу для выхода");
            Console.ReadKey();
        }
    }
}
