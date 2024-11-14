import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ImageBackground, TextInput, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import Menu from '../components/Menu';
import SearchIcon from '../assets/svg/SearchIcon';
import ArrowIcon from '../assets/svg/ArrowIcon';
import { useNavigation } from '@react-navigation/native';
import { DictionaryMeaningScreenNavigationProp, RootStackParamList } from '../../types';
import { Content } from './type';
import { getContent } from './repo';
import LinearGradient from 'react-native-linear-gradient';

const Dictionary: React.FC = () => {
  const [searchString, setSearchText] = useState('');
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState<number>(0);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const navigation = useNavigation<DictionaryMeaningScreenNavigationProp>();
  const [activeScreen, setActiveScreen] = useState<keyof RootStackParamList | null>('Dictionary');

  const fetchContents = async (reset = false) => {
    setLoading(true);
    try {
      const result = await getContent(searchString, offset, 10);
      const newContents = result.data;
      if (reset) {
        setContents(newContents);
        setOffset(0);
      } else {
        setContents((prevContents) => [...prevContents, ...newContents]);
      }


      if (newContents.length < 10) {
        setHasMore(false);
      }


      if (newContents.length === 10) {
        setOffset((prevOffset) => prevOffset + 10);
      }
    } catch (error) {
      setError('Failed to fetch contents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setOffset(0);
    setHasMore(true);
    fetchContents(true);
  }, [searchString]);

  const loadMoreData = () => {
    if (!loading && hasMore) {
      fetchContents();
    }
  };

  const navigateToMeaning = (contentId: number) => {
    navigation.navigate('DictionaryMeaning', { contentId });
  };

  return (
    <LinearGradient colors={['#6addd0', '#f7c188']} className="flex-1 justify-center items-center resize-cover">
      <View className="items-center mb-3 mt-8">
        <Text className="text-4xl font-black text-white">Dictionary</Text>
      </View>
      <View className="flex flex-row items-center justify-start bg-white rounded-lg px-4 mb-5 w-4/5 h-10">
        <TextInput
          className="flex-1 h-full text-[#999] text-base"
          placeholder="Search for a word"
          placeholderTextColor="#000"
          value={searchString}
          onChangeText={setSearchText}
        />
        <SearchIcon className="w-7 h-7" />
      </View>
      <View className="flex flex-row items-center mb-4 gap-16">
        <Text className="text-white text-2xl px-4 py-2 rounded-2xl" style={{
          backgroundColor: 'rgba(240, 240, 240, 0.4)'
        }}>Native</Text>
        <Text className="text-white text-2xl px-4 py-2 rounded-2xl" style={{
          backgroundColor: 'rgba(240, 240, 240, 0.4)'
        }}>English</Text>
      </View>
      <ScrollView
        contentContainerStyle={{ paddingHorizontal: 20 }}
        showsVerticalScrollIndicator={false}
        onScroll={({ nativeEvent }) => {
          const { layoutMeasurement, contentOffset, contentSize } = nativeEvent;


          if (layoutMeasurement.height + contentOffset.y >= contentSize.height - 50) {
            loadMoreData();
          }
        }}
        scrollEventThrottle={16}
      >
        {loading && offset === 0 ? (
          <ActivityIndicator size="large" />
        ) : contents.length > 0 ? (
          contents.map((c, index) => (
            <TouchableOpacity key={index} onPress={() => navigateToMeaning(c.contentID)}>
                <LinearGradient colors={['#f7c188', '#6addd0']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }} // Left to right gradient
                  className="rounded-lg py-3 px-5 mb-3  border border-[#FAF9F6]"
                >
                  <View className="flex flex-row items-center gap-x-4">
                    <Text className="text-xl text-center text-white w-[30%] font-bold">{c.contentText}</Text>
                    <ArrowIcon className="w-8 h-8 text-white" />
                    <Text className="text-xl text-center text-white w-[30%] font-bold italic">{c.englishTranslation}</Text>
                  </View>
                </LinearGradient>
            </TouchableOpacity>
          ))
        ) : (
          <Text className="text-white text-lg text-center">No words found</Text>
        )}
        {loading && offset > 0 && (
          <ActivityIndicator size="large" className="mt-4" />
        )}
      </ScrollView>
      <Menu activeScreen={activeScreen} />
    </LinearGradient>
  );
};

export default Dictionary;
